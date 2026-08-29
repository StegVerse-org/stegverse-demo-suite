from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SvDn1LivePreflightTaskTests(unittest.TestCase):
    def test_web_preflight_cannot_be_promoted_to_live_source_capture(self) -> None:
        data = json.loads((ROOT / "evidence/sv-dn1/preflight/2026-08-27-qwen3-8b-web-observation.json").read_text())
        self.assertEqual(data["retrieval_class"], "PUBLIC_WEB_PARSED_JSON")
        self.assertFalse(data["raw_response_bytes_captured"])
        self.assertIsNone(data["raw_response_sha256"])
        self.assertFalse(data["admissible_as_live_source_capture"])
        self.assertFalse(data["claims"]["live_source_capture"])
        self.assertFalse(data["claims"]["live_double_interlock_traversal"])
        self.assertFalse(data["claims"]["sdk_admitted"])
        self.assertFalse(data["claims"]["public_dashboard_live"])
        self.assertEqual(data["authority_effect"], "NONE")

    def test_preflight_records_real_public_model_identity_without_endorsement_claim(self) -> None:
        data = json.loads((ROOT / "evidence/sv-dn1/preflight/2026-08-27-qwen3-8b-web-observation.json").read_text())
        obs = data["parsed_observation"]
        self.assertEqual(obs["modelId"], "Qwen/Qwen3-8B")
        self.assertEqual(obs["sha"], "b968826d9c46dd6066d109eabc6255188de91218")
        self.assertFalse(obs["private"])
        self.assertFalse(obs["gated"])
        self.assertFalse(data["claims"]["hugging_face_endorsement_claimed"])
        self.assertFalse(data["claims"]["certification_claimed"])

    def test_resident_task_preserves_runtime_and_authority_boundaries(self) -> None:
        task = json.loads((ROOT / "tasks/SV-DN1-RESIDENT-OBSERVER-001.json").read_text())
        self.assertEqual(task["state"], "HANDOFF_READY_MACHINE_EXECUTION_PENDING")
        self.assertFalse(task["manual_execution_allowed"])
        self.assertEqual(task["target_refresh_hours"], 12)
        self.assertTrue(task["material_delta_refresh"])
        self.assertFalse(task["authority"]["github_actions_production_observer"])
        self.assertEqual(task["authority"]["github_token_runtime_authority"], "NONE")
        self.assertFalse(task["authority"]["repository_writeback_authority"])
        self.assertFalse(task["authority"]["governance_authority"])
        self.assertEqual(task["authority"]["credential_authority"], "TV/TVC")
        self.assertEqual(task["authority"]["authority_effect"], "NONE")
        self.assertEqual(task["execution_scope"], "RESIDENT_CAPTURE_AND_HF_SEMANTIC_EXCHANGE_ONLY")
        self.assertEqual(task["predecessor_task_id"], "SV-DN1-SOURCE-MATERIALIZATION-001")
        self.assertEqual(task["successor_task_id"], "SV-DN1-INTR-RUNTIME-001")
        self.assertEqual(
            task["current_blockers"],
            [
                "EXACT_PINNED_LOCAL_DEMO_SUITE_SOURCE_NOT_YET_OBSERVED",
                "CANONICAL_SCHEDULER_CLAIM_NOT_YET_BOUND",
                "SOVEREIGN_SV_DN1_RESIDENT_SOURCE_CAPTURE_RECEIPT_NOT_YET_OBSERVED",
            ],
        )
        self.assertNotIn("SDK_LIVE_ADMISSION_NOT_YET_OBSERVED", task["current_blockers"])
        self.assertNotIn("ROUTE_SPECIFIC_INTR_RUNTIME_RECEIPT_NOT_YET_OBSERVED", task["current_blockers"])
        self.assertFalse(task["success_predicates"].count("SDK binding_state=SDK_ADMITTED"))


if __name__ == "__main__":
    unittest.main()
