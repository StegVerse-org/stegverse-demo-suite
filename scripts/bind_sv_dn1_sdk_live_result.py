#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

CANONICAL_ROUTE_ID = "stegverse.route.canonical-governed.v1"
ROUTE_FIELDS = (
    "route_id",
    "lane_class",
    "routing_surface",
    "containment",
    "sandbox_required",
    "external_consequence_enabled",
)
STATE_BINDING_FIELDS = (
    "candidate",
    "judgment",
    "signal",
    "execution",
    "capability",
    "continuity",
    "approval",
    "permission_present",
)
MR_RE = re.compile(r"^MR-[A-F0-9]{16,64}$")


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def sha256_ref(value: Any) -> str:
    return "sha256:" + sha256_hex(value)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected object")
    return value


def normalize_return_projection(value: Mapping[str, Any]) -> dict[str, Any]:
    mode = str(value.get("mode") or "ALL").strip().upper()
    selected = list(value.get("transition_classes") or [])
    return {
        "mode": mode,
        "transition_classes": selected,
        "controls_user_return_only": True,
        "suppresses_master_records_custody": False,
        "erases_ecosystem_transitions": False,
        "grants_authority": False,
    }


def normalize_manifest_labels(value: Mapping[str, Any]) -> dict[str, Any]:
    mode = str(value.get("mode") or "NONE").strip().upper()
    defaults = mode != "NONE"
    return {
        "profile": "stegverse.manifest-labels.v1",
        "mode": mode,
        "sections": list(value.get("sections") or []),
        "include_field_descriptions": bool(value.get("include_field_descriptions", defaults)),
        "include_transition_class_labels": bool(value.get("include_transition_class_labels", defaults)),
        "include_receipt_class_labels": bool(value.get("include_receipt_class_labels", defaults)),
        "include_editability_labels": bool(value.get("include_editability_labels", defaults)),
        "include_authority_boundary_labels": bool(value.get("include_authority_boundary_labels", defaults)),
        "controls_return_explanation_only": True,
        "changes_governance_decision": False,
        "suppresses_master_records_custody": False,
        "grants_authority": False,
    }


def canonicalize_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = deepcopy(dict(manifest))
    canonical.setdefault("source_instance", None)
    canonical.setdefault("freshness", {})
    canonical.setdefault("context_refs", [])
    canonical.setdefault("canonicalization_profile", "steggate.jcs.v1")
    canonical.setdefault("attestation", None)
    canonical.setdefault("extensions", {})
    canonical["return_projection"] = normalize_return_projection(canonical.get("return_projection") or {})
    canonical["manifest_labels"] = normalize_manifest_labels(canonical.get("manifest_labels") or {})
    canonical["ingress_mode"] = "external_manifest"
    canonical["external_manifest_valid"] = True
    canonical["external_manifest_grants_authority"] = False
    canonical["master_records_transition_custody_independent_of_return_projection"] = True
    canonical["manifest_labels_change_governance"] = False
    canonical["canonical_manifest_sha256"] = sha256_hex(canonical)
    return canonical


def route_resolution(manifest: Mapping[str, Any]) -> dict[str, Any]:
    declaration = ((manifest.get("extensions") or {}).get("stegverse_route") or {})
    expected = {
        "route_id": CANONICAL_ROUTE_ID,
        "lane_class": "PRODUCTION_VALIDATION",
        "routing_surface": "CANONICAL_PRODUCTION",
        "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
        "sandbox_required": False,
        "external_consequence_enabled": False,
    }
    require(declaration == expected, "manifest route is not the canonical published production route")
    resolved = dict(expected)
    resolved["route_declaration_hash"] = sha256_hex(expected)
    return resolved


def governance_state_hash(request: Mapping[str, Any]) -> str:
    projection = {field: request.get(field) for field in STATE_BINDING_FIELDS}
    return sha256_hex(projection)


def bounded_request_id(source_output_id: str, digest: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in source_output_id)
    safe = safe.strip("-._") or "submission"
    return f"sdk-0b-{safe}-{digest[:16]}"[:80]


def expected_sdk_public_request(manifest: Mapping[str, Any]) -> dict[str, Any]:
    canonical = canonicalize_manifest(manifest)
    route = route_resolution(canonical)
    raw_request = deepcopy(canonical["extensions"]["stegverse_governance_request"])
    require(raw_request.get("candidate") == canonical.get("candidate"), "manifest/governance candidate mismatch")
    state_hash = governance_state_hash(raw_request)
    identity = {
        "manifest_profile": canonical["manifest_profile"],
        "manifest_profile_version": canonical["manifest_profile_version"],
        "source_framework": canonical["source_framework"],
        "source_instance": canonical.get("source_instance"),
        "source_output_id": canonical["source_output_id"],
        "canonical_manifest_sha256": canonical["canonical_manifest_sha256"],
        "ingress_mode": "external_manifest",
        "authority_effect": "NONE",
    }
    route_binding = {
        "route_id": route["route_id"],
        "route_declaration_hash": route["route_declaration_hash"],
        "state_binding_hash": state_hash,
        "route_substitution_permitted": False,
    }
    context = deepcopy(raw_request.get("declared_context") or {})
    context["sdk_ingress_manifest_identity"] = identity
    context["sdk_route_binding"] = route_binding
    raw_request["declared_context"] = context

    input_data: dict[str, Any] = {
        "ingress_manifest_identity": identity,
        "route_binding": route_binding,
    }
    if canonical.get("payload") is not None:
        input_data["payload"] = canonical["payload"]
    else:
        input_data["payload_commitment"] = canonical["payload_commitment"]

    request = {
        "schema_version": "1.0",
        "request_id": bounded_request_id(canonical["source_output_id"], canonical["canonical_manifest_sha256"]),
        "requester_label": canonical["source_framework"],
        "case_profile": "ordinary",
        "execution_provenance": {
            "route_id": route["route_id"],
            "route_declaration_hash": route["route_declaration_hash"],
            "lane_class": route["lane_class"],
            "routing_surface": route["routing_surface"],
            "containment": route["containment"],
            "sandbox_required": route["sandbox_required"],
            "sandbox_tier": "NONE",
            "origin_surface": "StegVerse-org/StegVerse-SDK:governance-0B",
            "external_consequence_enabled": route["external_consequence_enabled"],
            "third_party_host_required": False,
            "state_binding_hash": state_hash,
        },
        "input": {
            "steggate_request": raw_request,
            "input_data": input_data,
            "ingress_manifest_identity": identity,
            "route_binding": route_binding,
        },
        "return_projection": canonical["return_projection"]["mode"],
        "manifest_labels": canonical["manifest_labels"]["mode"] != "NONE",
        "authority_claim": False,
        "notes": (
            f"0B manifest {canonical['canonical_manifest_sha256']}; declared route resolved without substitution; "
            "validation does not grant authority"
        ),
    }
    # validate_public_inspection_request adds these absent optional fields.
    request["evaluation_declaration"] = None
    request.setdefault("requester_label", None)
    request.setdefault("notes", None)
    return request


def validate_result(candidate_packet: dict[str, Any], sdk_result: dict[str, Any]) -> dict[str, Any]:
    require(candidate_packet.get("schema_version") == "stegverse.sv-dn1.sdk-ingress-candidate/v1", "wrong candidate packet schema")
    require(candidate_packet.get("execution_readiness") == "READY_FOR_SDK_0B", "candidate is not READY_FOR_SDK_0B")
    require(candidate_packet.get("authority_effect") == "NONE", "candidate authority drift")
    require(isinstance(candidate_packet.get("intr_runtime_receipt"), dict), "authentic route-specific InTr receipt is required")

    claims = candidate_packet.get("claims") or {}
    require(claims.get("sdk_admitted") is False, "candidate already claims SDK admission")
    require(claims.get("governed_run_executed") is False, "candidate already claims governed execution")

    manifest = candidate_packet.get("manifest")
    require(isinstance(manifest, dict), "candidate manifest missing")
    canonical = canonicalize_manifest(manifest)
    expected_request = expected_sdk_public_request(manifest)
    expected_request_hash = sha256_ref(expected_request)
    route = route_resolution(canonical)
    state_hash = expected_request["execution_provenance"]["state_binding_hash"]

    require(sdk_result.get("schema") == "stegverse.sovereign-production-validation-result.v1", "wrong SDK result schema")
    require(sdk_result.get("request_id") == expected_request["request_id"], "SDK request identity mismatch")
    require(sdk_result.get("submitted_manifest_hash") == expected_request_hash, "SDK submitted request binding mismatch")
    require(sdk_result.get("declared_route_id") == CANONICAL_ROUTE_ID, "SDK route mismatch")
    require(sdk_result.get("route_declaration_hash") == route["route_declaration_hash"], "SDK route declaration hash mismatch")
    require(sdk_result.get("state_binding_hash") == state_hash, "SDK governance state binding mismatch")
    provenance = sdk_result.get("execution_provenance") or {}
    require(provenance.get("route_id") == CANONICAL_ROUTE_ID, "SDK execution provenance route mismatch")
    require(provenance.get("route_declaration_hash") == route["route_declaration_hash"], "SDK execution provenance declaration mismatch")
    require(provenance.get("state_binding_hash") == state_hash, "SDK execution provenance state mismatch")
    require(provenance.get("routing_surface") == "CANONICAL_PRODUCTION", "SDK execution did not use canonical production surface")
    require(provenance.get("lane_class") == "PRODUCTION_VALIDATION", "SDK execution lane mismatch")
    require(provenance.get("external_consequence_enabled") is False, "external consequence unexpectedly enabled")
    require(provenance.get("third_party_host_required") is False, "third-party host unexpectedly required")
    require(provenance.get("execution_host_class") == "SOVEREIGN_LOCAL", "SDK result is not from sovereign local execution")

    require(sdk_result.get("route_substitution_permitted") is False, "SDK result permits route substitution")
    require(sdk_result.get("route_substitution_occurred") is False, "SDK route substitution occurred")
    require(sdk_result.get("route_augmentation_permitted") is False, "SDK route augmentation unexpectedly permitted")
    require(sdk_result.get("configuration_not_augmentation") is True, "SDK configuration boundary not preserved")
    require(sdk_result.get("chain_verified") is True, "SDK result chain is not verified")
    require(sdk_result.get("transaction_identity_continuous") is True, "transaction identity continuity failed")
    require(sdk_result.get("master_records_custody_status") == "RECORDED", "Master Records exact-run custody not recorded")
    require(sdk_result.get("external_side_effect") is False, "SV-DN-1 evaluation produced external side effect")
    require(sdk_result.get("third_party_host_required") is False, "SDK result requires third-party host")
    require(isinstance(sdk_result.get("transaction_id"), str) and sdk_result["transaction_id"], "transaction_id missing")
    require(isinstance(sdk_result.get("route_manifest_id"), str) and sdk_result["route_manifest_id"], "route_manifest_id missing")
    receipts = sdk_result.get("route_receipt_ids")
    require(isinstance(receipts, list) and receipts and all(isinstance(x, str) and x for x in receipts), "route receipt ids missing")
    require(sdk_result.get("route_transition_count") == len(receipts), "route transition count mismatch")
    require(isinstance(sdk_result.get("route_receipt_chain_head"), str) and sdk_result["route_receipt_chain_head"], "route receipt chain head missing")
    mr = sdk_result.get("manifest_receipt_id")
    require(isinstance(mr, str) and MR_RE.fullmatch(mr) is not None, "canonical manifest receipt id missing")
    governance = sdk_result.get("governance_state")
    require(governance in ("ALLOW", "DENY", "REVIEW", "FAIL_CLOSED"), "unsupported governance state")

    result_hash = sdk_result.get("result_binding_hash")
    body = {k: deepcopy(v) for k, v in sdk_result.items() if k != "result_binding_hash"}
    require(result_hash == sha256_ref(body), "SDK result binding hash mismatch")

    return {
        "canonical_manifest": canonical,
        "expected_request": expected_request,
        "manifest_hash": "sha256:" + canonical["canonical_manifest_sha256"],
        "sdk_result_binding_hash": result_hash,
        "route_declaration_hash": route["route_declaration_hash"],
        "state_binding_hash": state_hash,
    }


def bind(candidate_packet: dict[str, Any], sdk_result: dict[str, Any]) -> dict[str, Any]:
    checked = validate_result(candidate_packet, sdk_result)
    exchange = candidate_packet["exchange"]
    return {
        "schema_version": "stegverse.sv-dn1.sdk-admission/v1",
        "state": "SDK_ADMITTED",
        "exchange_id": exchange["exchange_id"],
        "sdk_request_id": sdk_result["request_id"],
        "sdk_result_binding_hash": checked["sdk_result_binding_hash"],
        "sdk_intake": {
            "manifest_hash": checked["manifest_hash"],
            "intake_receipt_id": sdk_result["manifest_receipt_id"],
            "binding_state": "SDK_ADMITTED",
        },
        "governance_state": sdk_result["governance_state"],
        "route": {
            "route_id": sdk_result["declared_route_id"],
            "route_declaration_hash": sdk_result["route_declaration_hash"],
            "state_binding_hash": sdk_result["state_binding_hash"],
            "route_receipt_ids": list(sdk_result["route_receipt_ids"]),
            "route_receipt_chain_head": sdk_result["route_receipt_chain_head"],
            "route_transition_count": sdk_result["route_transition_count"],
            "transaction_id": sdk_result["transaction_id"],
            "transaction_identity_continuous": True,
        },
        "custody": {
            "master_records_custody_status": "RECORDED",
            "chain_verified": True,
        },
        "claims": {
            "sdk_governed_run_observed": True,
            "master_records_custody_observed": True,
            "certification_claimed": False,
            "hugging_face_endorsement_claimed": False,
            "canonical_interlock_adoption_claimed": False,
            "production_interlock_runtime_activation_claimed": False,
        },
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--sdk-result", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    admission = bind(load_object(Path(args.candidate)), load_object(Path(args.sdk_result)))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(admission, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": admission["state"],
        "exchange_id": admission["exchange_id"],
        "manifest_receipt_id": admission["sdk_intake"]["intake_receipt_id"],
        "governance_state": admission["governance_state"],
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
