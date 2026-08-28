#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / "config" / "sv_dn1_public_readiness.json").read_text(encoding="utf-8"))
ALLOWED_STATES = set(POLICY["lane_states"])
REQUIRED_LANES = tuple(POLICY["required_production_lanes"])


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _lane(state: str = "NOT_OBSERVED", *, evidence_refs=(), known_errors=(), unknowns=()) -> dict[str, Any]:
    require(state in ALLOWED_STATES, f"unsupported lane state: {state}")
    return {
        "state": state,
        "evidence_refs": list(dict.fromkeys(str(x) for x in evidence_refs if x)),
        "known_errors": list(dict.fromkeys(str(x) for x in known_errors if x)),
        "unknowns": list(dict.fromkeys(str(x) for x in unknowns if x)),
        "authority_effect": "NONE",
    }


def _normalize_explicit_lane(name: str, raw: Mapping[str, Any]) -> dict[str, Any]:
    state = raw.get("state")
    require(state in ALLOWED_STATES, f"{name}: invalid lane state {state}")
    require(raw.get("authority_effect", "NONE") == "NONE", f"{name}: authority effect forbidden")
    refs = raw.get("evidence_refs") or []
    errors = raw.get("known_errors") or []
    unknowns = raw.get("unknowns") or []
    for label, value in (("evidence_refs", refs), ("known_errors", errors), ("unknowns", unknowns)):
        require(isinstance(value, list) and all(isinstance(x, str) for x in value), f"{name}: {label} must be string list")
    if state in {"PASS", "FAIL", "DEGRADED"}:
        require(bool(refs), f"{name}: observed state {state} requires evidence_refs")
    if state == "FAIL":
        require(bool(errors), f"{name}: FAIL requires known_errors")
    if state == "UNKNOWN":
        require(bool(unknowns), f"{name}: UNKNOWN requires unknowns")
    return _lane(state, evidence_refs=refs, known_errors=errors, unknowns=unknowns)


def build(
    exchange: Mapping[str, Any],
    receipt: Mapping[str, Any],
    explicit_lane_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    explicit_lane_evidence = explicit_lane_evidence or {}
    unknown_keys = sorted(set(explicit_lane_evidence) - set(REQUIRED_LANES))
    require(not unknown_keys, "unknown production lanes: " + ",".join(unknown_keys))

    live = receipt.get("sdk_intake", {}).get("binding_state") == "SDK_ADMITTED"
    observation_class = "LIVE" if live else "FIXTURE"

    lanes = {
        name: _lane(
            "NOT_OBSERVED",
            unknowns=[f"{name} has no authentic route-specific production observation in this packet"],
        )
        for name in REQUIRED_LANES
    }

    # Fixture/source evidence may prove deterministic source behavior, but it must
    # never be promoted into a production-lane PASS in this observation object.
    if not live:
        lanes["hf_facing_interlock"]["evidence_refs"] = [
            exchange.get("far_side_receipt", {}).get("transformation_hash"),
        ]
        lanes["stegverse_interlock"]["evidence_refs"] = [
            receipt.get("exchange_id"),
        ]
        lanes["public_projection"]["evidence_refs"] = [
            receipt.get("receipt_id"),
        ]

    for name, raw in explicit_lane_evidence.items():
        require(isinstance(raw, Mapping), f"{name}: lane evidence must be object")
        lanes[name] = _normalize_explicit_lane(name, raw)

    # A live SDK binding itself is admissible evidence for the SDK ingress lane,
    # but it does not prove any other production lane.
    if live and "sdk_ingress" not in explicit_lane_evidence:
        lanes["sdk_ingress"] = _lane(
            "PASS",
            evidence_refs=[
                receipt["sdk_intake"].get("manifest_hash"),
                receipt["sdk_intake"].get("intake_receipt_id"),
            ],
        )

    # Never allow a fixture packet to claim observed production lane states.
    if observation_class == "FIXTURE":
        for name, lane in lanes.items():
            require(
                lane["state"] in {"NOT_OBSERVED", "NOT_APPLICABLE"},
                f"fixture cannot promote production lane {name} to {lane['state']}",
            )

    known_errors = []
    unknowns = []
    for name in REQUIRED_LANES:
        lane = lanes[name]
        known_errors.extend(f"{name}: {x}" for x in lane["known_errors"])
        unknowns.extend(f"{name}: {x}" for x in lane["unknowns"])

    unresolved_states = {"FAIL", "DEGRADED", "UNKNOWN", "NOT_REACHED", "NOT_OBSERVED"}
    first_unresolved = next(
        (name for name in REQUIRED_LANES if lanes[name]["state"] in unresolved_states),
        None,
    )

    hard_withhold = observation_class != "LIVE"
    if any(lane["state"] == "NOT_OBSERVED" for lane in lanes.values()):
        hard_withhold = True
    if any(lane["state"] == "NOT_REACHED" for lane in lanes.values()):
        hard_withhold = True

    observed_with_limitations = observation_class == "LIVE" and not hard_withhold and (
        bool(known_errors)
        or bool(unknowns)
        or any(lane["state"] in {"FAIL", "DEGRADED", "UNKNOWN"} for lane in lanes.values())
    )
    if hard_withhold:
        publication_state = "WITHHELD"
    elif observed_with_limitations:
        publication_state = "PUBLIC_WITH_LIMITATIONS"
    else:
        publication_state = "PUBLIC_OBSERVED"

    claims = {
        "all_lanes_pass": all(lane["state"] in {"PASS", "NOT_APPLICABLE"} for lane in lanes.values()),
        "zero_known_defects": not known_errors,
        "zero_unknowns": not unknowns,
        "production_perfection_claimed": False,
        "certification_claimed": False,
    }

    return {
        "schema_version": "stegverse.sv-dn1.production-pipeline-observation/v1",
        "profile_id": "SV-DN-1",
        "observation_class": observation_class,
        "publication_state": publication_state,
        "production_stack_is_subject_of_observation": True,
        "lanes": lanes,
        "known_errors": known_errors,
        "unknowns": unknowns,
        "first_unresolved_pipeline_boundary": first_unresolved,
        "claims": claims,
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--lane-evidence")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    lane_evidence = None
    if args.lane_evidence:
        lane_evidence = json.loads(Path(args.lane_evidence).read_text(encoding="utf-8"))
    result = build(exchange, receipt, lane_evidence)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_PRODUCTION_PIPELINE_OBSERVATION_BUILT",
        "observation_class": result["observation_class"],
        "publication_state": result["publication_state"],
        "first_unresolved_pipeline_boundary": result["first_unresolved_pipeline_boundary"],
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
