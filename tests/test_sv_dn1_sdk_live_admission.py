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


HF = load("sv_dn1_hf_sdk_bridge_test", "scripts/sv_dn1_hf_interlock.py")
BUILD = load("sv_dn1_sdk_manifest_builder_test", "scripts/build_sv_dn1_sdk_ingress_manifest.py")
VALIDATE = load("sv_dn1_sdk_manifest_validator_test", "scripts/validate_sv_dn1_sdk_ingress_candidate.py")


class SvDn1SdkLiveAdmissionBridgeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.native = json.loads((ROOT / "fixtures/sv_dn1/hf_model_baseline.json").read_text(encoding="utf-8"))
        raw = json.dumps(self.native, separators=(",", ":"), sort_keys=False).encode("utf-8")
        self.capture = {
            "schema_version": "stegverse.sv-dn1.source-capture/v1",
            "capture_id": "sha256:" + hashlib.sha256(b"synthetic-live-shaped-capture").hexdigest(),
            "source_system": "huggingface",
            "requested_url": "https://huggingface.co/api/models/stegverse-fixture/example-open-model",
            "final_url": "https://huggingface.co/api/models/stegverse-fixture/example-open-model",
            "observed_at": "2026-08-27T23:50:00Z",
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
        self.exchange = HF.build_exchange(
            self.native,
            self.capture["final_url"],
            self.capture["observed_at"],
        )
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

    def test_builds_exact_current_sdk_0b_route_without_admission_claim(self) -> None:
        packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-27T23:51:00Z"
        )
        self.assertEqual(VALIDATE.validate(packet), [])
        manifest = packet["manifest"]
        self.assertEqual(manifest["manifest_profile"], "stegverse.ingress-manifest.v1")
        self.assertEqual(manifest["extensions"]["stegverse_route"], BUILD.ROUTE)
        self.assertEqual(
            manifest["extensions"]["stegverse_governance_request"]["candidate"],
            manifest["candidate"],
        )
        self.assertFalse(packet["claims"]["sdk_admitted"])
        self.assertFalse(packet["claims"]["governed_run_executed"])
        self.assertFalse(packet["claims"]["steggate_allow_claimed"])
        self.assertEqual(packet["authority_effect"], "NONE")

    def test_manifest_hashes_match_sdk_canonical_json_contract(self) -> None:
        packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-27T23:51:00Z"
        )
        manifest = packet["manifest"]
        self.assertEqual(
            manifest["hashes"]["payload_sha256"],
            BUILD.sha256_hex(manifest["payload"]),
        )
        self.assertEqual(
            manifest["hashes"]["candidate_sha256"],
            BUILD.sha256_hex(manifest["candidate"]),
        )

    def test_missing_runtime_inputs_remain_explicit(self) -> None:
        packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-27T23:51:00Z"
        )
        missing = packet["manifest"]["extensions"]["stegverse_governance_request"]["signal"]["missing_inputs"]
        self.assertEqual(
            missing,
            ["route_specific_intr_runtime_receipt", "sdk_live_admission_receipt"],
        )

    def test_rejects_fixture_or_nonresident_state(self) -> None:
        bad = copy.deepcopy(self.resident)
        bad["state"] = "FIXTURE_BOUND"
        with self.assertRaises(ValueError):
            BUILD.build_ingress_candidate(bad, self.capture, self.exchange, "2026-08-27T23:51:00Z")

    def test_rejects_capture_exchange_source_substitution(self) -> None:
        bad_capture = copy.deepcopy(self.capture)
        bad_capture["final_url"] = "https://huggingface.co/api/models/other/model"
        with self.assertRaises(ValueError):
            BUILD.build_ingress_candidate(self.resident, bad_capture, self.exchange, "2026-08-27T23:51:00Z")

    def test_tampered_candidate_fails_validation(self) -> None:
        packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-27T23:51:00Z"
        )
        packet["manifest"]["candidate"]["target"] = "tampered"
        blockers = VALIDATE.validate(packet)
        self.assertIn("candidate_hash_mismatch", blockers)
        self.assertIn("governance_candidate_mismatch", blockers)

    def test_validator_preserves_pre_admission_nonclaims(self) -> None:
        packet = BUILD.build_ingress_candidate(
            self.resident, self.capture, self.exchange, "2026-08-27T23:51:00Z"
        )
        packet["claims"]["sdk_admitted"] = True
        self.assertIn("premature_claim:sdk_admitted", VALIDATE.validate(packet))


if __name__ == "__main__":
    unittest.main()
