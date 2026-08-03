#!/usr/bin/env python3
"""Deterministic governed digital-rights demonstration evaluator.

The evaluator intentionally uses only the Python standard library. It validates the
committed demonstration fixture, denies unauthorized or retroactive split changes,
reconstructs the active rights state at each usage event, allocates royalties, and
emits a canonical SHA-256 receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

TOTAL_BASIS_POINTS = 10_000
ALLOWED_DECISIONS = {"ALLOW", "DENY"}
ALLOWED_TERMINAL_STATES = {
    "COMPLETE",
    "BLOCKED",
    "RETRY",
    "REVIEW_REQUIRED",
    "FAILED",
    "CLAIMED",
    "SUPERSEDED",
    "MERGED",
}


class ValidationError(ValueError):
    """Raised when required evidence is absent, malformed, or contradictory."""


@dataclass(frozen=True)
class TransitionDecision:
    transition_id: str
    decision: str
    reason: str
    effective_at: str
    proposed_shares_basis_points: Mapping[str, int]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "decision": self.decision,
            "reason": self.reason,
            "effective_at": self.effective_at,
            "proposed_shares_basis_points": dict(self.proposed_shares_basis_points),
        }


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def parse_timestamp(value: str, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValidationError(f"{field_name} must be a non-empty RFC3339 timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{field_name} is not a valid RFC3339 timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise ValidationError(f"{field_name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def require_mapping(value: Any, field_name: str) -> MutableMapping[str, Any]:
    if not isinstance(value, dict):
        raise ValidationError(f"{field_name} must be an object")
    return value


def require_sequence(value: Any, field_name: str) -> Sequence[Any]:
    if not isinstance(value, list):
        raise ValidationError(f"{field_name} must be an array")
    return value


def validate_shares(shares: Mapping[str, Any], participant_ids: Iterable[str], field_name: str) -> Dict[str, int]:
    expected_ids = set(participant_ids)
    actual_ids = set(shares.keys())
    if actual_ids != expected_ids:
        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)
        raise ValidationError(f"{field_name} participant mismatch; missing={missing}, extra={extra}")

    normalized: Dict[str, int] = {}
    for participant_id, amount in shares.items():
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise ValidationError(f"{field_name}.{participant_id} must be an integer basis-point amount")
        if amount < 0 or amount > TOTAL_BASIS_POINTS:
            raise ValidationError(f"{field_name}.{participant_id} must be between 0 and {TOTAL_BASIS_POINTS}")
        normalized[participant_id] = amount

    if sum(normalized.values()) != TOTAL_BASIS_POINTS:
        raise ValidationError(f"{field_name} must sum to {TOTAL_BASIS_POINTS} basis points")
    return normalized


def validate_contract_shape(case: Mapping[str, Any]) -> Tuple[List[str], Dict[str, int]]:
    required_top_level = {
        "schema_version",
        "goal_id",
        "asset",
        "participants",
        "initial_rights",
        "royalty_policy",
        "transitions",
        "usage_periods",
    }
    missing = sorted(required_top_level - set(case.keys()))
    if missing:
        raise ValidationError(f"missing required top-level fields: {missing}")

    if case["schema_version"] != "1.0.0":
        raise ValidationError("schema_version must be 1.0.0")
    if case["goal_id"] != "GDRC-DEMO-001":
        raise ValidationError("goal_id must be GDRC-DEMO-001")

    asset = require_mapping(case["asset"], "asset")
    for field in ("asset_id", "title", "asset_type", "components"):
        if field not in asset:
            raise ValidationError(f"asset.{field} is required")
    components = require_sequence(asset["components"], "asset.components")
    if not components:
        raise ValidationError("asset.components must not be empty")
    component_ids = set()
    for index, raw_component in enumerate(components):
        component = require_mapping(raw_component, f"asset.components[{index}]")
        for field in ("component_id", "component_type", "sha256"):
            if field not in component:
                raise ValidationError(f"asset.components[{index}].{field} is required")
        if component["component_id"] in component_ids:
            raise ValidationError(f"duplicate component_id: {component['component_id']}")
        component_ids.add(component["component_id"])
        digest = component["sha256"]
        if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
            raise ValidationError(f"asset.components[{index}].sha256 must be lowercase 64-character hex")

    raw_participants = require_sequence(case["participants"], "participants")
    if len(raw_participants) < 2:
        raise ValidationError("participants must contain at least two parties")
    participant_ids: List[str] = []
    for index, raw_participant in enumerate(raw_participants):
        participant = require_mapping(raw_participant, f"participants[{index}]")
        participant_id = participant.get("participant_id")
        if not isinstance(participant_id, str) or not participant_id:
            raise ValidationError(f"participants[{index}].participant_id is required")
        if participant_id in participant_ids:
            raise ValidationError(f"duplicate participant_id: {participant_id}")
        if participant.get("can_sign_split_change") is not True:
            raise ValidationError(f"participants[{index}] must explicitly permit split-change signatures")
        participant_ids.append(participant_id)

    initial_rights = require_mapping(case["initial_rights"], "initial_rights")
    parse_timestamp(initial_rights.get("effective_at"), "initial_rights.effective_at")
    change_policy = require_mapping(initial_rights.get("change_policy"), "initial_rights.change_policy")
    if change_policy.get("required_signers") != "all_participants":
        raise ValidationError("initial_rights.change_policy.required_signers must be all_participants")
    if change_policy.get("retroactive_changes_allowed") is not False:
        raise ValidationError("retroactive_changes_allowed must be false")
    initial_shares = validate_shares(
        require_mapping(initial_rights.get("shares_basis_points"), "initial_rights.shares_basis_points"),
        participant_ids,
        "initial_rights.shares_basis_points",
    )

    policy = require_mapping(case["royalty_policy"], "royalty_policy")
    if policy.get("currency") != "USD":
        raise ValidationError("royalty_policy.currency must be USD for this bounded demo")
    if policy.get("rounding") != "largest_remainder":
        raise ValidationError("royalty_policy.rounding must be largest_remainder")

    require_sequence(case["transitions"], "transitions")
    usage_periods = require_sequence(case["usage_periods"], "usage_periods")
    if not usage_periods:
        raise ValidationError("usage_periods must not be empty")
    return participant_ids, initial_shares


def evaluate_transitions(
    case: Mapping[str, Any], participant_ids: Sequence[str]
) -> Tuple[List[TransitionDecision], List[Tuple[datetime, Dict[str, int], str]]]:
    initial_rights = case["initial_rights"]
    initial_effective = parse_timestamp(initial_rights["effective_at"], "initial_rights.effective_at")
    state_timeline: List[Tuple[datetime, Dict[str, int], str]] = [
        (initial_effective, dict(initial_rights["shares_basis_points"]), "initial_rights")
    ]
    required_signatures = set(participant_ids)
    decisions: List[TransitionDecision] = []
    prior_effective = initial_effective

    for index, raw_transition in enumerate(case["transitions"]):
        transition = require_mapping(raw_transition, f"transitions[{index}]")
        transition_id = transition.get("transition_id")
        if not isinstance(transition_id, str) or not transition_id:
            raise ValidationError(f"transitions[{index}].transition_id is required")
        submitted_at = parse_timestamp(transition.get("submitted_at"), f"transitions[{index}].submitted_at")
        effective_at = parse_timestamp(transition.get("effective_at"), f"transitions[{index}].effective_at")
        proposed = validate_shares(
            require_mapping(
                transition.get("proposed_shares_basis_points"),
                f"transitions[{index}].proposed_shares_basis_points",
            ),
            participant_ids,
            f"transitions[{index}].proposed_shares_basis_points",
        )
        signatures_raw = require_sequence(transition.get("signatures"), f"transitions[{index}].signatures")
        signatures = set(signatures_raw)
        if not all(isinstance(value, str) for value in signatures_raw):
            raise ValidationError(f"transitions[{index}].signatures must contain participant IDs")
        if not signatures.issubset(required_signatures):
            unknown = sorted(signatures - required_signatures)
            raise ValidationError(f"transitions[{index}] contains unknown signatures: {unknown}")

        if signatures != required_signatures:
            decision = "DENY"
            reason = "MISSING_REQUIRED_SIGNATURES"
        elif effective_at < submitted_at or effective_at < prior_effective:
            decision = "DENY"
            reason = "RETROACTIVE_CHANGE_PROHIBITED"
        else:
            decision = "ALLOW"
            reason = "AUTHORIZED_NON_RETROACTIVE_AMENDMENT"
            state_timeline.append((effective_at, proposed, transition_id))
            prior_effective = effective_at

        expected_decision = transition.get("expected_decision")
        expected_reason = transition.get("expected_reason")
        if expected_decision not in ALLOWED_DECISIONS:
            raise ValidationError(f"transitions[{index}].expected_decision must be ALLOW or DENY")
        if decision != expected_decision or reason != expected_reason:
            raise ValidationError(
                f"transition expectation mismatch for {transition_id}: expected "
                f"{expected_decision}/{expected_reason}, calculated {decision}/{reason}"
            )

        decisions.append(
            TransitionDecision(
                transition_id=transition_id,
                decision=decision,
                reason=reason,
                effective_at=transition["effective_at"],
                proposed_shares_basis_points=proposed,
            )
        )

    state_timeline.sort(key=lambda item: item[0])
    return decisions, state_timeline


def active_state_at(
    occurred_at: datetime, state_timeline: Sequence[Tuple[datetime, Dict[str, int], str]]
) -> Tuple[Dict[str, int], str]:
    active_shares: Dict[str, int] | None = None
    source = ""
    for effective_at, shares, state_source in state_timeline:
        if effective_at <= occurred_at:
            active_shares = dict(shares)
            source = state_source
        else:
            break
    if active_shares is None:
        raise ValidationError("usage occurred before any rights state was effective")
    return active_shares, source


def allocate_largest_remainder(total_cents: int, shares: Mapping[str, int]) -> Dict[str, int]:
    if isinstance(total_cents, bool) or not isinstance(total_cents, int) or total_cents < 0:
        raise ValidationError("distributable_amount_cents must be a non-negative integer")

    floor_allocations: Dict[str, int] = {}
    remainders: List[Tuple[int, str]] = []
    allocated = 0
    for participant_id in sorted(shares):
        numerator = total_cents * shares[participant_id]
        floor_value, remainder = divmod(numerator, TOTAL_BASIS_POINTS)
        floor_allocations[participant_id] = floor_value
        allocated += floor_value
        remainders.append((remainder, participant_id))

    cents_remaining = total_cents - allocated
    for _, participant_id in sorted(remainders, key=lambda item: (-item[0], item[1]))[:cents_remaining]:
        floor_allocations[participant_id] += 1

    if sum(floor_allocations.values()) != total_cents:
        raise ValidationError("allocation failed conservation check")
    return floor_allocations


def evaluate_usage(
    case: Mapping[str, Any],
    participant_ids: Sequence[str],
    state_timeline: Sequence[Tuple[datetime, Dict[str, int], str]],
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    prior_usage_time: datetime | None = None
    for index, raw_usage in enumerate(case["usage_periods"]):
        usage = require_mapping(raw_usage, f"usage_periods[{index}]")
        usage_id = usage.get("usage_id")
        if not isinstance(usage_id, str) or not usage_id:
            raise ValidationError(f"usage_periods[{index}].usage_id is required")
        occurred_at = parse_timestamp(usage.get("occurred_at"), f"usage_periods[{index}].occurred_at")
        if prior_usage_time is not None and occurred_at <= prior_usage_time:
            raise ValidationError("usage_periods must be strictly chronological")
        prior_usage_time = occurred_at
        streams = usage.get("streams")
        if isinstance(streams, bool) or not isinstance(streams, int) or streams < 0:
            raise ValidationError(f"usage_periods[{index}].streams must be a non-negative integer")

        active_shares, rights_source = active_state_at(occurred_at, state_timeline)
        expected_shares = validate_shares(
            require_mapping(
                usage.get("expected_shares_basis_points"),
                f"usage_periods[{index}].expected_shares_basis_points",
            ),
            participant_ids,
            f"usage_periods[{index}].expected_shares_basis_points",
        )
        if active_shares != expected_shares:
            raise ValidationError(
                f"historical reconstruction mismatch for {usage_id}: "
                f"expected {expected_shares}, calculated {active_shares}"
            )

        amount_cents = usage.get("distributable_amount_cents")
        allocation = allocate_largest_remainder(amount_cents, active_shares)
        expected_allocation = require_mapping(
            usage.get("expected_allocation_cents"),
            f"usage_periods[{index}].expected_allocation_cents",
        )
        normalized_expected_allocation: Dict[str, int] = {}
        if set(expected_allocation) != set(participant_ids):
            raise ValidationError(f"usage_periods[{index}].expected_allocation_cents participant mismatch")
        for participant_id, cents in expected_allocation.items():
            if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
                raise ValidationError(
                    f"usage_periods[{index}].expected_allocation_cents.{participant_id} must be non-negative integer"
                )
            normalized_expected_allocation[participant_id] = cents
        if allocation != normalized_expected_allocation:
            raise ValidationError(
                f"allocation mismatch for {usage_id}: expected {normalized_expected_allocation}, calculated {allocation}"
            )

        results.append(
            {
                "usage_id": usage_id,
                "occurred_at": usage["occurred_at"],
                "rights_source": rights_source,
                "active_shares_basis_points": active_shares,
                "streams": streams,
                "distributable_amount_cents": amount_cents,
                "allocation_cents": allocation,
                "conservation_check": sum(allocation.values()) == amount_cents,
            }
        )
    return results


def validate_claim_state(task_state: Mapping[str, Any], now: datetime | None = None) -> Dict[str, Any]:
    if task_state.get("task_id") != "GDRC-DEMO-001":
        raise ValidationError("task_state.task_id must be GDRC-DEMO-001")
    state = task_state.get("state")
    if state not in ALLOWED_TERMINAL_STATES:
        raise ValidationError(f"task_state.state is not recognized: {state}")
    created_at = parse_timestamp(task_state.get("claim_created_at"), "task_state.claim_created_at")
    expires_at = parse_timestamp(task_state.get("claim_expires_at"), "task_state.claim_expires_at")
    if expires_at <= created_at:
        raise ValidationError("task_state.claim_expires_at must be after claim_created_at")
    observed_at = now or datetime.now(timezone.utc)
    stale = state == "CLAIMED" and observed_at > expires_at
    return {
        "task_id": task_state["task_id"],
        "state": state,
        "claimant": task_state.get("claimant"),
        "claim_created_at": task_state["claim_created_at"],
        "claim_expires_at": task_state["claim_expires_at"],
        "stale": stale,
        "release_condition": task_state.get("release_condition"),
    }


def evaluate_case(case: Mapping[str, Any], task_state: Mapping[str, Any] | None = None) -> Dict[str, Any]:
    participant_ids, _ = validate_contract_shape(case)
    decisions, state_timeline = evaluate_transitions(case, participant_ids)
    allocations = evaluate_usage(case, participant_ids, state_timeline)

    receipt_core: Dict[str, Any] = {
        "receipt_version": "1.0.0",
        "goal_id": case["goal_id"],
        "asset_id": case["asset"]["asset_id"],
        "source_case_sha256": sha256_hex(case),
        "transition_decisions": [decision.to_dict() for decision in decisions],
        "usage_allocations": allocations,
        "historical_states": [
            {
                "effective_at": effective_at.isoformat().replace("+00:00", "Z"),
                "source": source,
                "shares_basis_points": shares,
            }
            for effective_at, shares, source in state_timeline
        ],
        "checks": {
            "shares_conserved": True,
            "royalties_conserved": all(item["conservation_check"] for item in allocations),
            "unauthorized_transition_denied": any(
                item.decision == "DENY" and item.reason == "MISSING_REQUIRED_SIGNATURES" for item in decisions
            ),
            "authorized_future_amendment_applied": any(
                item.decision == "ALLOW" and item.reason == "AUTHORIZED_NON_RETROACTIVE_AMENDMENT"
                for item in decisions
            ),
            "historical_period_preserved": allocations[0]["rights_source"] == "initial_rights",
        },
        "status": "COMPLETE",
    }
    if task_state is not None:
        receipt_core["task_claim"] = validate_claim_state(task_state)
    receipt_core["receipt_sha256"] = sha256_hex(receipt_core)
    return receipt_core


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"required file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{path} must contain a JSON object")
    return value


def validate_schema_document(schema: Mapping[str, Any]) -> None:
    if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValidationError("schema document must declare JSON Schema draft 2020-12")
    if schema.get("$id") != "https://stegverse.org/schemas/governed-digital-rights-demo.schema.json":
        raise ValidationError("schema document has unexpected $id")
    required = schema.get("required")
    if not isinstance(required, list) or "transitions" not in required or "usage_periods" not in required:
        raise ValidationError("schema document does not bind the core transition and usage evidence")


def write_receipt(receipt: Mapping[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Path to demo_case.json")
    parser.add_argument("--schema", required=True, type=Path, help="Path to the JSON Schema contract")
    parser.add_argument("--task-state", type=Path, help="Optional persistent task/claim state")
    parser.add_argument("--output", required=True, type=Path, help="Receipt output path")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        case = load_json(args.input)
        schema = load_json(args.schema)
        validate_schema_document(schema)
        task_state = load_json(args.task_state) if args.task_state else None
        receipt = evaluate_case(case, task_state=task_state)
        write_receipt(receipt, args.output)
    except ValidationError as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    print(json.dumps({"status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
