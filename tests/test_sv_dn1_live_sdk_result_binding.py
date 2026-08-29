from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


HF = load("sv_dn1_hf_live_result_binding_test", "scripts/sv_dn1_hf_interlock.py")
BUILD = load("sv_dn1_build_live_result_binding_test", "scripts/build_sv_dn1_sdk_ingress_manifest.py")
BIND = load("sv_dn1_live_result_binding_test", "scripts/bind_sv_dn1_sdk_live_result.py")
EVAL = load("sv_dn1_evaluator_live_result_binding_test", "scripts/sv_dn1_evaluator.py")


class SvDn1LiveSdkResultBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.native = json.loads((ROOT / "fixtures/sv_dn1/hf_model_baseline.json").read_text())
        raw = json.dumps(self.native, separators=(",", ":"), sort_keys=False).encode()
        self.capture = {
            "schema_version": "stegverse.sv-dn1.source-capture/v1",
            "capture_id": "sha256:" + hashlib.sha256(b"live-shaped-capture").hexdigest(),
            "source_system": "huggingface",
            "requested_url": "https://huggingface.co/api/models/stegverse-fixture/example-open-model",
            "final_url": "https://huggingface.co/api/models/stegverse-fixture/example-open-model",
            "observed_at": "2026-08-28T00:30:00Z",
            "http_status": 200,
            "content_type": "application/json",
            "raw_sha256": "sha256:" + hashlib.sha256(raw).hexdigest(),
            "raw_size": len(raw),
            "parsed_json": self.native,
            "claims": {
                "public_source_only": True,
                "credential_used": False,
                "hugging_face_endorsement_claimed": False,
                "live_interlock_traversal_claimed": False,
            },
            "authority_effect": "NONE",
        }
        self.exchange = HF.build_exchange(self.native, self.capture["final_url"], self.capture["observed_at"])
        self.resident = {
            "schema": "stegverse.sv-dn1.resident-source-observer-receipt/v0.1",
            "task_id": "SV-DN1-RESIDENT-OBSERVER-001",
            "state": "COMPLETE",
            "transition_id": "SV_DN1_RESIDENT_SOURCE_CAPTURE_COMPLETE",
            "claim_id": "synthetic-test-claim",
            "worker_id": "sv-dn1-resident-observer-worker",
            "raw_response_sha256": self.capture["raw_sha256"],
            "raw_response_sha256_present": True,
            "semantic_exchange_id": self.exchange["exchange_id"],
            "semantic_exchange_valid": True,
            "credential_used": False,
            "github_token_used": False,
            "repository_writeback_performed": False,
            "sdk_admitted": False,
            "hugging_face_endorsement_claimed": False,
            "authority_effect": "OBSERVATION_ONLY_NO_NEW_AUTHORITY",
        }
        intr_body = {
            "schema_version": "stegverse.sv-dn1.intr-runtime-receipt/v1",
            "route_id": "SV-DN-1-HF-PUBLIC",
            "exchange_id": self.exchange["exchange_id"],
            "state": "COMPLETE",
            "observed_at": "2026-08-28T00:30:30Z",
            "transport_profile": "stegverse.universal-intr.adjacent-hop/v1",
            "source_transform_hash": self.exchange["far_side_receipt"]["transformation_hash"],
            "previous_receipt_hash": self.exchange["intr"]["previous_receipt_hash"],
            "destination_validation": "PASS",
            "lineage_verified": True,
            "claims": {
                "canonical_protocol_adopted": True,
                "universal_intr_policy_id": "STEGVERSE-UNIVERSAL-INTR-TRANSPORT-001",
                "boundary_from": "EXTERNAL_SYSTEM",
                "boundary_to": "STEGOS_ECOSYSTEM",
                "interlock_required_per_hop": True,
                "receipt_hash_chain_required": True,
                "runtime_activation_claimed": False,
                "production_interlock_runtime_activated": False,
                "sdk_admitted": False,
                "hugging_face_endorsement_claimed": False,
                "credential_used": False,
            },
            "authority_effect": "NONE",
        }
        intr_body["receipt_hash"] = BUILD.sha256_ref(intr_body)
        self.intr = intr_body
        self.packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-28T00:31:00Z", self.intr
        )
        self.sdk_result = self.make_sdk_result()

    def make_sdk_result(self, governance_state: str = "ALLOW") -> dict:
        request = BIND.expected_sdk_public_request(self.packet["manifest"])
        canonical = BIND.canonicalize_manifest(self.packet["manifest"])
        route = BIND.route_resolution(canonical)
        body = {
            "schema": "stegverse.sovereign-production-validation-result.v1",
            "request_id": request["request_id"],
            "case_profile": "ordinary",
            "evaluation_declaration": None,
            "testing_contract_version": "stegverse.sdk-testing-noninterference.v1",
            "configuration_not_augmentation": True,
            "route_augmentation_permitted": False,
            "route_substitution_permitted": False,
            "route_substitution_occurred": False,
            "evaluator_identity_is_decision_input": False,
            "declared_expected_observation_is_decision_input": False,
            "unsupported_capability_behavior": "REJECT_BEFORE_EXECUTION",
            "submitted_manifest_hash": BIND.sha256_ref(request),
            "governance_request_hash": "sha256:" + "1" * 64,
            "declared_route_id": BIND.CANONICAL_ROUTE_ID,
            "route_declaration_hash": route["route_declaration_hash"],
            "state_binding_hash": request["execution_provenance"]["state_binding_hash"],
            "execution_provenance": {
                **request["execution_provenance"],
                "execution_host_class": "SOVEREIGN_LOCAL",
                "execution_host_identity": "synthetic-sovereign-test",
                "third_party_host_required": False,
            },
            "transaction_id": "TX-SV-DN1-SYNTHETIC-001",
            "route_manifest_id": "RM-SV-DN1-SYNTHETIC-001",
            "route_receipt_ids": ["RR-SYNTHETIC-001", "RR-SYNTHETIC-002"],
            "route_transition_count": 2,
            "route_receipt_chain_head": "sha256:" + "2" * 64,
            "manifest_receipt_id": "MR-" + "A" * 64,
            "governance_state": governance_state,
            "chain_verified": True,
            "transaction_identity_continuous": True,
            "master_records_custody_status": "RECORDED",
            "external_side_effect": False,
            "third_party_host_required": False,
            "declared_execution_context_consumed_by_canonical_runtime": False,
        }
        body["result_binding_hash"] = BIND.sha256_ref(body)
        return body

    def test_binds_exact_canonical_sdk_result_to_sdk_admitted_evaluator_input(self) -> None:
        admission = BIND.bind(self.packet, self.sdk_result)
        self.assertEqual(admission["state"], "SDK_ADMITTED")
        self.assertEqual(admission["sdk_intake"]["binding_state"], "SDK_ADMITTED")
        self.assertEqual(admission["sdk_intake"]["intake_receipt_id"], self.sdk_result["manifest_receipt_id"])
        self.assertEqual(admission["governance_state"], "ALLOW")
        self.assertTrue(admission["custody"]["chain_verified"])
        self.assertEqual(admission["custody"]["master_records_custody_status"], "RECORDED")
        self.assertFalse(admission["claims"]["certification_claimed"])
        self.assertFalse(admission["claims"]["canonical_interlock_adoption_claimed"])

    def test_sdk_admission_can_feed_existing_sv_dn1_evaluator(self) -> None:
        admission = BIND.bind(self.packet, self.sdk_result)
        receipt = EVAL.evaluate(self.exchange, admission)
        self.assertEqual(receipt["sdk_intake"]["binding_state"], "SDK_ADMITTED")
        self.assertTrue(receipt["claims"]["live_double_interlock_traversal_claimed"])

    def test_governance_deny_is_preserved_not_hidden(self) -> None:
        sdk = self.make_sdk_result("DENY")
        admission = BIND.bind(self.packet, sdk)
        self.assertEqual(admission["state"], "SDK_ADMITTED")
        self.assertEqual(admission["governance_state"], "DENY")

    def test_request_binding_tamper_fails_closed(self) -> None:
        bad = copy.deepcopy(self.sdk_result)
        bad["submitted_manifest_hash"] = "sha256:" + "0" * 64
        bad["result_binding_hash"] = BIND.sha256_ref({k: v for k, v in bad.items() if k != "result_binding_hash"})
        with self.assertRaises(ValueError):
            BIND.bind(self.packet, bad)

    def test_missing_custody_fails_closed(self) -> None:
        bad = copy.deepcopy(self.sdk_result)
        bad["master_records_custody_status"] = "NOT_RECORDED"
        bad["result_binding_hash"] = BIND.sha256_ref({k: v for k, v in bad.items() if k != "result_binding_hash"})
        with self.assertRaises(ValueError):
            BIND.bind(self.packet, bad)

    def test_route_substitution_fails_closed(self) -> None:
        bad = copy.deepcopy(self.sdk_result)
        bad["route_substitution_occurred"] = True
        bad["result_binding_hash"] = BIND.sha256_ref({k: v for k, v in bad.items() if k != "result_binding_hash"})
        with self.assertRaises(ValueError):
            BIND.bind(self.packet, bad)

    def test_sdk_result_hash_tamper_fails_closed(self) -> None:
        bad = copy.deepcopy(self.sdk_result)
        bad["result_binding_hash"] = "sha256:" + "0" * 64
        with self.assertRaises(ValueError):
            BIND.bind(self.packet, bad)

    def test_nonready_candidate_cannot_be_promoted(self) -> None:
        blocked = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-28T00:31:00Z"
        )
        with self.assertRaises(ValueError):
            BIND.bind(blocked, self.sdk_result)


if __name__ == "__main__":
    unittest.main()
