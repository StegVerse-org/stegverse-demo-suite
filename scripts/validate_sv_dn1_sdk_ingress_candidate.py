#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

EXPECTED_ROUTE = {
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


def intr_receipt_body(receipt: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in receipt.items() if k != "receipt_hash"}


def validate_intr_receipt(receipt: dict[str, Any], exchange: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if receipt.get("schema_version") != INTR_RECEIPT_SCHEMA:
        blockers.append("intr_wrong_schema")
    if receipt.get("route_id") != INTR_ROUTE_ID:
        blockers.append("intr_wrong_route")
    if receipt.get("state") != "COMPLETE":
        blockers.append("intr_not_complete")
    if receipt.get("exchange_id") != exchange.get("exchange_id"):
        blockers.append("intr_exchange_mismatch")
    if receipt.get("source_transform_hash") != exchange.get("far_side_receipt", {}).get("transformation_hash"):
        blockers.append("intr_source_transform_mismatch")
    if receipt.get("previous_receipt_hash") != exchange.get("intr", {}).get("previous_receipt_hash"):
        blockers.append("intr_previous_receipt_mismatch")
    if receipt.get("destination_validation") != "PASS":
        blockers.append("intr_destination_not_validated")
    if receipt.get("lineage_verified") is not True:
        blockers.append("intr_lineage_not_verified")
    if not isinstance(receipt.get("transport_profile"), str) or not receipt.get("transport_profile"):
        blockers.append("intr_transport_profile_missing")
    if not isinstance(receipt.get("observed_at"), str) or not receipt.get("observed_at"):
        blockers.append("intr_observed_at_missing")
    claims = receipt.get("claims") or {}
    if claims.get("canonical_protocol_adopted") is not False:
        blockers.append("intr_canonical_adoption_claim_forbidden")
    if claims.get("production_interlock_runtime_activated") is not False:
        blockers.append("intr_global_runtime_activation_claim_forbidden")
    if claims.get("sdk_admitted") is not False:
        blockers.append("intr_premature_sdk_claim")
    if claims.get("hugging_face_endorsement_claimed") is not False:
        blockers.append("intr_external_endorsement_claim_forbidden")
    if claims.get("credential_used") is not False:
        blockers.append("intr_credential_use_forbidden")
    if receipt.get("authority_effect") != "NONE":
        blockers.append("intr_authority_effect_forbidden")
    if receipt.get("receipt_hash") != sha256_ref(intr_receipt_body(receipt)):
        blockers.append("intr_receipt_hash_mismatch")
    return blockers


def validate(packet: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if packet.get("schema_version") != "stegverse.sv-dn1.sdk-ingress-candidate/v1":
        blockers.append("wrong_packet_schema")
    if packet.get("authority_effect") != "NONE":
        blockers.append("authority_effect_forbidden")
    readiness = packet.get("execution_readiness")
    if readiness not in ("BLOCKED_ON_ROUTE_SPECIFIC_INTR", "READY_FOR_SDK_0B"):
        blockers.append("execution_readiness_invalid")

    claims = packet.get("claims") or {}
    for key in (
        "sdk_admitted",
        "governed_run_executed",
        "steggate_allow_claimed",
        "master_records_custody_claimed",
        "live_dashboard_published",
        "hugging_face_endorsement_claimed",
    ):
        if claims.get(key) is not False:
            blockers.append(f"premature_claim:{key}")

    manifest = packet.get("manifest")
    if not isinstance(manifest, dict):
        return sorted(set(blockers + ["manifest_missing"]))
    if manifest.get("manifest_profile") != "stegverse.ingress-manifest.v1":
        blockers.append("wrong_manifest_profile")
    if str(manifest.get("manifest_profile_version") or "") != "1":
        blockers.append("wrong_manifest_profile_version")
    if manifest.get("source_framework") != "StegVerse-org/stegverse-demo-suite:SV-DN-1":
        blockers.append("wrong_source_framework")

    payload = manifest.get("payload")
    candidate = manifest.get("candidate")
    hashes = manifest.get("hashes") or {}
    if not isinstance(payload, dict):
        blockers.append("payload_missing")
    elif hashes.get("payload_sha256") != sha256_hex(payload):
        blockers.append("payload_hash_mismatch")
    if not isinstance(candidate, dict):
        blockers.append("candidate_missing")
    elif hashes.get("candidate_sha256") != sha256_hex(candidate):
        blockers.append("candidate_hash_mismatch")

    extensions = manifest.get("extensions")
    if not isinstance(extensions, dict):
        blockers.append("extensions_missing")
    else:
        route = extensions.get("stegverse_route")
        if route != EXPECTED_ROUTE:
            blockers.append("route_declaration_mismatch")
        request = extensions.get("stegverse_governance_request")
        if not isinstance(request, dict):
            blockers.append("governance_request_missing")
        else:
            if request.get("candidate") != candidate:
                blockers.append("governance_candidate_mismatch")
            context = request.get("declared_context") or {}
            if context.get("sdk_admission_claimed") is not False:
                blockers.append("sdk_admission_claim_forbidden")
            if context.get("hugging_face_endorsement_claimed") is not False:
                blockers.append("external_endorsement_claim_forbidden")
            if context.get("authority_effect") != "NONE":
                blockers.append("governance_context_authority_drift")

            signal = request.get("signal") or {}
            transformations = signal.get("transformations")
            if not isinstance(transformations, list) or not all(isinstance(x, str) for x in transformations):
                blockers.append("sdk_signal_transformations_not_string_list")
            missing = signal.get("missing_inputs")
            if not isinstance(missing, list) or not all(isinstance(x, str) for x in missing):
                blockers.append("missing_inputs_not_explicit")
                missing = []
            if "sdk_live_admission_receipt" in missing:
                blockers.append("post_execution_receipt_misclassified_as_input")
            if signal.get("uncertainty_state") not in ("bounded", "material", "unknown"):
                blockers.append("sdk_uncertainty_state_invalid")

            continuity = request.get("continuity") or {}
            intr = packet.get("intr_runtime_receipt")
            if readiness == "BLOCKED_ON_ROUTE_SPECIFIC_INTR":
                if intr is not None:
                    blockers.append("blocked_packet_has_intr_receipt")
                if missing != ["route_specific_intr_runtime_receipt"]:
                    blockers.append("blocked_packet_missing_input_mismatch")
                if signal.get("uncertainty_state") != "material":
                    blockers.append("blocked_packet_uncertainty_must_be_material")
                if continuity.get("required") is not True:
                    blockers.append("continuity_required_missing")
                if continuity.get("previous_receipt_verified") is True:
                    blockers.append("blocked_packet_premature_continuity_verification")
            elif readiness == "READY_FOR_SDK_0B":
                if not isinstance(intr, dict):
                    blockers.append("ready_packet_intr_receipt_missing")
                else:
                    blockers.extend(validate_intr_receipt(intr, packet.get("exchange") or {}))
                if missing:
                    blockers.append("ready_packet_has_material_missing_inputs")
                if signal.get("uncertainty_state") != "bounded":
                    blockers.append("ready_packet_uncertainty_not_bounded")
                if continuity.get("required") is not True:
                    blockers.append("continuity_required_missing")
                if continuity.get("previous_receipt_verified") is not True:
                    blockers.append("continuity_receipt_not_verified")
                if isinstance(intr, dict) and continuity.get("previous_receipt_hash") != intr.get("receipt_hash"):
                    blockers.append("continuity_receipt_hash_mismatch")
                if isinstance(intr, dict):
                    if context.get("intr_runtime_receipt_id") != intr.get("receipt_hash"):
                        blockers.append("intr_context_receipt_mismatch")
                    if context.get("intr_transport_profile") != intr.get("transport_profile"):
                        blockers.append("intr_context_transport_mismatch")

            execution = request.get("execution") or {}
            if candidate and candidate.get("parameters", {}).get("external_side_effect") is not False:
                blockers.append("external_side_effect_forbidden")
            if EXPECTED_ROUTE["external_consequence_enabled"] is not False:
                blockers.append("route_external_consequence_drift")
            if execution.get("credential_authority") not in (None, "TV/TVC"):
                blockers.append("credential_authority_drift")

    resident = packet.get("resident_receipt") or {}
    capture = packet.get("source_capture") or {}
    exchange = packet.get("exchange") or {}
    if resident.get("transition_id") != "SV_DN1_RESIDENT_SOURCE_CAPTURE_COMPLETE":
        blockers.append("resident_live_transition_missing")
    if resident.get("raw_response_sha256_present") is not True:
        blockers.append("raw_response_hash_not_proven")
    if resident.get("semantic_exchange_valid") is not True:
        blockers.append("semantic_exchange_not_proven")
    if resident.get("sdk_admitted") is not False:
        blockers.append("resident_sdk_state_not_pre_admission")
    if capture.get("raw_sha256") != resident.get("raw_response_sha256"):
        blockers.append("capture_resident_hash_mismatch")
    if exchange.get("exchange_id") != resident.get("semantic_exchange_id"):
        blockers.append("exchange_resident_identity_mismatch")
    if exchange.get("source_object", {}).get("native_ref") != capture.get("final_url"):
        blockers.append("source_ref_mismatch")
    if exchange.get("source_object", {}).get("observed_at") != capture.get("observed_at"):
        blockers.append("observed_at_mismatch")
    if exchange.get("raw_evidence", {}).get("preserved_native_fields") != capture.get("parsed_json"):
        blockers.append("parsed_source_exchange_mismatch")
    return sorted(set(blockers))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("packet")
    args = ap.parse_args()
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    blockers = validate(packet)
    result = {
        "state": "SDK_0B_CANDIDATE_SOURCE_VALID" if not blockers else "REJECTED",
        "execution_readiness": packet.get("execution_readiness"),
        "blockers": blockers,
        "sdk_admitted": False,
        "governed_run_executed": False,
        "authority_effect": "NONE",
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
