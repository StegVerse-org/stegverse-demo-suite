#!/usr/bin/env python3
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

ROUTE = {
    "route_id": "stegverse.route.canonical-governed.v1",
    "lane_class": "PRODUCTION_VALIDATION",
    "routing_surface": "CANONICAL_PRODUCTION",
    "containment": "PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE",
    "sandbox_required": False,
    "external_consequence_enabled": False,
}

INTR_RECEIPT_SCHEMA = "stegverse.sv-dn1.intr-runtime-receipt/v1"
INTR_ROUTE_ID = "SV-DN-1-HF-PUBLIC"


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
    require(isinstance(value, dict), f"{path}: root must be object")
    return value


def validate_live_inputs(
    resident_receipt: dict[str, Any],
    capture: dict[str, Any],
    exchange: dict[str, Any],
) -> None:
    require(resident_receipt.get("state") == "COMPLETE", "resident receipt must be COMPLETE")
    require(
        resident_receipt.get("transition_id") == "SV_DN1_RESIDENT_SOURCE_CAPTURE_COMPLETE",
        "wrong resident transition",
    )
    require(resident_receipt.get("raw_response_sha256_present") is True, "raw response hash not proven")
    require(resident_receipt.get("semantic_exchange_valid") is True, "semantic exchange not proven")
    require(resident_receipt.get("credential_used") is False, "credentialed capture is not admitted")
    require(resident_receipt.get("github_token_used") is False, "GitHub token use is not admitted")
    require(resident_receipt.get("repository_writeback_performed") is False, "repository writeback is not admitted")
    require(resident_receipt.get("sdk_admitted") is False, "pre-admission bridge cannot consume already-promoted SDK state")
    require(resident_receipt.get("hugging_face_endorsement_claimed") is False, "external endorsement claim forbidden")

    require(capture.get("schema_version") == "stegverse.sv-dn1.source-capture/v1", "wrong capture schema")
    require(capture.get("source_system") == "huggingface", "wrong capture source system")
    require(capture.get("raw_sha256") == resident_receipt.get("raw_response_sha256"), "capture/resident raw hash mismatch")
    claims = capture.get("claims") or {}
    require(claims.get("credential_used") is False, "capture claims credential use")
    require(claims.get("hugging_face_endorsement_claimed") is False, "capture claims endorsement")

    require(exchange.get("schema_version") == "stegverse.sv-dn1.interlock-exchange/v1", "wrong exchange schema")
    require(exchange.get("source_system") == "huggingface", "wrong exchange source system")
    require(exchange.get("exchange_id") == resident_receipt.get("semantic_exchange_id"), "exchange/resident identity mismatch")
    require(exchange.get("source_object", {}).get("native_ref") == capture.get("final_url"), "capture/exchange source ref mismatch")
    require(exchange.get("source_object", {}).get("observed_at") == capture.get("observed_at"), "capture/exchange observation time mismatch")
    require(exchange.get("raw_evidence", {}).get("preserved_native_fields") == capture.get("parsed_json"), "capture/exchange native JSON mismatch")
    require(exchange.get("far_side_receipt", {}).get("authority_effect") == "NONE", "far-side authority drift")
    require(exchange.get("intr", {}).get("authority_effect") == "NONE", "InTr authority drift")


def intr_receipt_body(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: deepcopy(v) for k, v in receipt.items() if k != "receipt_hash"}


def validate_intr_runtime_receipt(
    intr_receipt: dict[str, Any],
    exchange: dict[str, Any],
) -> None:
    require(intr_receipt.get("schema_version") == INTR_RECEIPT_SCHEMA, "wrong InTr runtime receipt schema")
    require(intr_receipt.get("route_id") == INTR_ROUTE_ID, "wrong SV-DN-1 InTr route")
    require(intr_receipt.get("state") == "COMPLETE", "InTr runtime receipt must be COMPLETE")
    require(intr_receipt.get("exchange_id") == exchange.get("exchange_id"), "InTr/exchange identity mismatch")
    require(
        intr_receipt.get("source_transform_hash") == exchange.get("far_side_receipt", {}).get("transformation_hash"),
        "InTr source transformation hash mismatch",
    )
    require(
        intr_receipt.get("previous_receipt_hash") == exchange.get("intr", {}).get("previous_receipt_hash"),
        "InTr previous receipt hash mismatch",
    )
    require(intr_receipt.get("destination_validation") == "PASS", "InTr destination validation not PASS")
    require(intr_receipt.get("lineage_verified") is True, "InTr lineage not verified")
    require(isinstance(intr_receipt.get("observed_at"), str) and intr_receipt["observed_at"], "InTr observed_at missing")
    require(isinstance(intr_receipt.get("transport_profile"), str) and intr_receipt["transport_profile"], "InTr transport profile missing")
    claims = intr_receipt.get("claims") or {}
    require(claims.get("canonical_protocol_adopted") is True, "canonical Universal InTr policy adoption must be acknowledged")
    require(claims.get("universal_intr_policy_id") == "STEGVERSE-UNIVERSAL-INTR-TRANSPORT-001", "wrong Universal InTr policy")
    require(claims.get("boundary_from") == "EXTERNAL_SYSTEM", "wrong Universal InTr source boundary")
    require(claims.get("boundary_to") == "STEGOS_ECOSYSTEM", "wrong Universal InTr destination boundary")
    require(claims.get("interlock_required_per_hop") is True, "Universal InTr requires Interlock per hop")
    require(claims.get("receipt_hash_chain_required") is True, "Universal InTr requires chained hop receipts")
    require(claims.get("runtime_activation_claimed") is False, "route receipt may not claim global Universal InTr runtime activation")
    require(
        claims.get("production_interlock_runtime_activated") is False,
        "SV-DN-1 adjacent hop may not claim global production Interlock activation",
    )
    require(claims.get("sdk_admitted") is False, "pre-SDK InTr receipt may not claim SDK admission")
    require(claims.get("hugging_face_endorsement_claimed") is False, "InTr receipt may not claim Hugging Face endorsement")
    require(claims.get("credential_used") is False, "credentialed InTr traversal is not admitted")
    require(intr_receipt.get("authority_effect") == "NONE", "InTr receipt authority drift")
    require(intr_receipt.get("receipt_hash") == sha256_ref(intr_receipt_body(intr_receipt)), "InTr receipt hash mismatch")


def build_candidate(exchange: dict[str, Any]) -> dict[str, Any]:
    source = exchange["source_object"]
    return {
        "actor_class": "sv_dn1_public_evaluator",
        "action": "evaluate_model_distribution_neutrality",
        "target": f"{source['native_id']}@{source.get('native_revision') or 'unknown'}",
        "scope": "public_distribution_observation",
        "parameters": {
            "profile_id": "SV-DN-1",
            "source_system": "huggingface",
            "native_id": source["native_id"],
            "native_revision": source.get("native_revision"),
            "exchange_id": exchange["exchange_id"],
            "external_side_effect": False,
        },
    }


def build_governance_request(
    candidate: dict[str, Any],
    resident_receipt: dict[str, Any],
    capture: dict[str, Any],
    exchange: dict[str, Any],
    intr_receipt: dict[str, Any] | None,
) -> dict[str, Any]:
    evidence_refs = [
        resident_receipt["raw_response_sha256"],
        exchange["exchange_id"],
        exchange["semantic_mapping"]["ruleset_hash"],
        exchange["far_side_receipt"]["transformation_hash"],
    ]
    missing_inputs: list[str] = []
    continuity: dict[str, Any] = {"required": True}
    if intr_receipt is None:
        missing_inputs.append("route_specific_intr_runtime_receipt")
    else:
        evidence_refs.append(intr_receipt["receipt_hash"])
        continuity.update({
            "previous_receipt_verified": True,
            "previous_receipt_hash": intr_receipt["receipt_hash"],
        })

    return {
        "candidate": deepcopy(candidate),
        "judgment": {
            "refusal_available": True,
            "operator_recoverability": "available",
            "workload_state": "supported",
            "time_pressure": "normal",
            "isolation_state": "supported",
            "evidence_refs": evidence_refs,
        },
        "signal": {
            "admitted_signal_refs": evidence_refs,
            "excluded_signal_refs": [],
            "transformations": [exchange["far_side_receipt"]["transformation_hash"]],
            "missing_inputs": missing_inputs,
            "uncertainty_state": "bounded" if intr_receipt is not None else "material",
            "reference_state_hash": exchange["raw_evidence"]["source_sha256"].removeprefix("sha256:"),
            "expected_reference_state_hash": exchange["raw_evidence"]["source_sha256"].removeprefix("sha256:"),
            "reconstruction_available": True,
            "transformation_provenance_complete": True,
        },
        "execution": {
            "actor_authority_current": True,
            "policy_current": True,
            "delegation_current": True,
            "evidence_current": True,
            "affected_entity_conditions_represented": True,
            "recoverability_profile": "recoverable",
            "validity_window_open": True,
            "policy_ref": "SV-DN-1/public-evaluation/v1",
            "delegation_ref": "SV-DN-1/non-authorizing-evaluation-only",
            "evidence_refs": evidence_refs,
        },
        "capability": {"allowed": True},
        "continuity": continuity,
        "approval": {"required": False},
        "permission_present": True,
        "declared_context": {
            "evaluation_profile": "SV-DN-1",
            "source_capture_id": capture["capture_id"],
            "raw_response_sha256": capture["raw_sha256"],
            "exchange_id": exchange["exchange_id"],
            "mapping_profile": exchange["semantic_mapping"]["profile"],
            "semantic_transformation": {
                "ruleset_hash": exchange["semantic_mapping"]["ruleset_hash"],
                "transformation_hash": exchange["far_side_receipt"]["transformation_hash"],
            },
            "intr_runtime_receipt_id": intr_receipt.get("receipt_hash") if intr_receipt else None,
            "intr_transport_profile": intr_receipt.get("transport_profile") if intr_receipt else None,
            "universal_intr_policy_id": (intr_receipt.get("claims") or {}).get("universal_intr_policy_id") if intr_receipt else None,
            "universal_intr_boundary_from": (intr_receipt.get("claims") or {}).get("boundary_from") if intr_receipt else None,
            "universal_intr_boundary_to": (intr_receipt.get("claims") or {}).get("boundary_to") if intr_receipt else None,
            "external_side_effect": False,
            "sdk_admission_claimed": False,
            "hugging_face_endorsement_claimed": False,
            "authority_effect": "NONE",
        },
    }


def build_ingress_candidate(
    resident_receipt: dict[str, Any],
    capture: dict[str, Any],
    exchange: dict[str, Any],
    created_at: str,
    intr_receipt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    validate_live_inputs(resident_receipt, capture, exchange)
    if intr_receipt is not None:
        validate_intr_runtime_receipt(intr_receipt, exchange)
    candidate = build_candidate(exchange)
    governance_request = build_governance_request(candidate, resident_receipt, capture, exchange, intr_receipt)
    payload: dict[str, Any] = {
        "schema_version": "stegverse.sv-dn1.sdk-live-evidence/v1",
        "profile_id": "SV-DN-1",
        "source_capture": {
            "capture_id": capture["capture_id"],
            "source_system": capture["source_system"],
            "requested_url": capture["requested_url"],
            "final_url": capture["final_url"],
            "observed_at": capture["observed_at"],
            "http_status": capture["http_status"],
            "content_type": capture["content_type"],
            "raw_sha256": capture["raw_sha256"],
            "raw_size": capture["raw_size"],
        },
        "semantic_exchange": {
            "exchange_id": exchange["exchange_id"],
            "native_id": exchange["source_object"]["native_id"],
            "native_revision": exchange["source_object"]["native_revision"],
            "mapping_profile": exchange["semantic_mapping"]["profile"],
            "ruleset_hash": exchange["semantic_mapping"]["ruleset_hash"],
            "transformation_hash": exchange["far_side_receipt"]["transformation_hash"],
        },
        "resident_observer": {
            "task_id": resident_receipt["task_id"],
            "worker_id": resident_receipt["worker_id"],
            "claim_id": resident_receipt["claim_id"],
            "transition_id": resident_receipt["transition_id"],
            "authority_effect": resident_receipt["authority_effect"],
        },
    }
    if intr_receipt is not None:
        payload["intr_runtime"] = {
            "receipt_hash": intr_receipt["receipt_hash"],
            "route_id": intr_receipt["route_id"],
            "exchange_id": intr_receipt["exchange_id"],
            "transport_profile": intr_receipt["transport_profile"],
            "observed_at": intr_receipt["observed_at"],
            "lineage_verified": intr_receipt["lineage_verified"],
            "authority_effect": intr_receipt["authority_effect"],
        }

    manifest = {
        "manifest_profile": "stegverse.ingress-manifest.v1",
        "manifest_profile_version": "1",
        "source_framework": "StegVerse-org/stegverse-demo-suite:SV-DN-1",
        "source_instance": "resident-public-observer",
        "source_output_id": f"SV-DN1-{exchange['exchange_id'].split(':', 1)[-1][:24]}",
        "created_at": created_at,
        "freshness": {
            "status": "observed",
            "source_observed_at": capture["observed_at"],
        },
        "payload": payload,
        "candidate": candidate,
        "declared_intent": "Evaluate the exact admitted public model-distribution observation under SV-DN-1 without external side effects.",
        "requested_consequence": "Produce a governed evaluation record only; do not mutate the external source or grant certification.",
        "context_refs": [
            capture["capture_id"],
            exchange["exchange_id"],
            resident_receipt["raw_response_sha256"],
        ] + ([intr_receipt["receipt_hash"]] if intr_receipt else []),
        "canonicalization_profile": "steggate.jcs.v1",
        "hashes": {
            "payload_sha256": sha256_hex(payload),
            "candidate_sha256": sha256_hex(candidate),
        },
        "attestation": None,
        "extensions": {
            "stegverse_route": dict(ROUTE),
            "stegverse_governance_request": governance_request,
        },
        "return_projection": {"mode": "ALL", "transition_classes": []},
        "manifest_labels": {
            "profile": "stegverse.manifest-labels.v1",
            "mode": "ALL",
            "sections": [],
            "include_field_descriptions": True,
            "include_transition_class_labels": True,
            "include_receipt_class_labels": True,
            "include_editability_labels": True,
            "include_authority_boundary_labels": True,
        },
    }
    return {
        "schema_version": "stegverse.sv-dn1.sdk-ingress-candidate/v1",
        "execution_readiness": "READY_FOR_SDK_0B" if intr_receipt is not None else "BLOCKED_ON_ROUTE_SPECIFIC_INTR",
        "resident_receipt": resident_receipt,
        "source_capture": capture,
        "exchange": exchange,
        "intr_runtime_receipt": intr_receipt,
        "manifest": manifest,
        "claims": {
            "sdk_admitted": False,
            "governed_run_executed": False,
            "steggate_allow_claimed": False,
            "master_records_custody_claimed": False,
            "live_dashboard_published": False,
            "hugging_face_endorsement_claimed": False,
        },
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resident-receipt", required=True)
    ap.add_argument("--source-capture", required=True)
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--intr-receipt")
    ap.add_argument("--created-at", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    intr_receipt = load_object(Path(args.intr_receipt)) if args.intr_receipt else None
    packet = build_ingress_candidate(
        load_object(Path(args.resident_receipt)),
        load_object(Path(args.source_capture)),
        load_object(Path(args.exchange)),
        args.created_at,
        intr_receipt,
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_SDK_0B_MANIFEST_PREPARED",
        "source_output_id": packet["manifest"]["source_output_id"],
        "execution_readiness": packet["execution_readiness"],
        "sdk_admitted": False,
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
