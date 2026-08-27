from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
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


HF = load("sv_dn1_hf_interlock_test", "scripts/sv_dn1_hf_interlock.py")
DEST = load("sv_dn1_dest_interlock_test", "scripts/sv_dn1_stegverse_interlock.py")
EVAL = load("sv_dn1_evaluator_test", "scripts/sv_dn1_evaluator.py")
DASH = load("sv_dn1_dashboard_test", "scripts/render_sv_dn1_dashboard.py")


class SvDn1DoubleInterlockTests(unittest.TestCase):
    def setUp(self) -> None:
        self.native = json.loads((ROOT / "fixtures/sv_dn1/hf_model_baseline.json").read_text(encoding="utf-8"))
        self.exchange = HF.build_exchange(
            self.native,
            "https://huggingface.co/stegverse-fixture/example-open-model",
            "2026-08-27T12:00:00Z",
        )

    def test_source_adapter_is_deterministic_and_preserves_native(self) -> None:
        again = HF.build_exchange(
            self.native,
            "https://huggingface.co/stegverse-fixture/example-open-model",
            "2026-08-27T12:00:00Z",
        )
        self.assertEqual(self.exchange, again)
        self.assertEqual(self.exchange["source_system"], "huggingface")
        self.assertEqual(self.exchange["far_side_receipt"]["authority_effect"], "NONE")
        self.assertEqual(self.exchange["intr"]["authority_effect"], "NONE")
        self.assertEqual(self.exchange["raw_evidence"]["preserved_native_fields"], self.native)
        self.assertIn("downloads", self.exchange["raw_evidence"]["unmapped_fields"])
        self.assertIn("fixture_only", self.exchange["raw_evidence"]["unmapped_fields"])

    def test_lossy_projection_is_explicit_and_native_is_preserved(self) -> None:
        lossy = self.exchange["semantic_mapping"]["lossy_transformations"]
        self.assertEqual(len(lossy), 1)
        self.assertEqual(lossy[0]["rule_id"], "HF-FILES-001")
        self.assertTrue(lossy[0]["native_preserved"])
        self.assertIn("siblings", self.exchange["raw_evidence"]["preserved_native_fields"])

    def test_destination_admits_valid_fixture_without_claiming_sdk_live(self) -> None:
        admission = DEST.bind_fixture_intake(self.exchange)
        self.assertEqual(admission["state"], "ADMITTED_FOR_FIXTURE_EVALUATION")
        self.assertEqual(admission["sdk_intake"]["binding_state"], "FIXTURE_BOUND")
        self.assertEqual(admission["authority_effect"], "NONE")

    def test_source_substitution_fails_closed(self) -> None:
        altered = copy.deepcopy(self.exchange)
        altered["raw_evidence"]["preserved_native_fields"]["likes"] = 999
        admission = DEST.bind_fixture_intake(altered)
        self.assertEqual(admission["state"], "REJECTED")
        self.assertIn("native_source_hash_mismatch", admission["blockers"])

    def test_semantic_transformation_tamper_fails_closed(self) -> None:
        altered = copy.deepcopy(self.exchange)
        altered["semantic"]["artifact"]["license"] = "proprietary"
        admission = DEST.bind_fixture_intake(altered)
        self.assertEqual(admission["state"], "REJECTED")
        self.assertIn("transformation_hash_mismatch", admission["blockers"])

    def test_silent_loss_fails_closed(self) -> None:
        altered = copy.deepcopy(self.exchange)
        altered["semantic_mapping"]["lossy_transformations"][0]["native_preserved"] = False
        admission = DEST.bind_fixture_intake(altered)
        self.assertEqual(admission["state"], "REJECTED")
        self.assertIn("silent_loss_forbidden", admission["blockers"])

    def test_evaluator_preserves_unknowns_and_nonclaims(self) -> None:
        admission = DEST.bind_fixture_intake(self.exchange)
        receipt = EVAL.evaluate(self.exchange, admission)
        self.assertEqual(receipt["authority_effect"], "NONE")
        self.assertGreater(receipt["summary"]["unknown"], 0)
        self.assertEqual(receipt["dimensions"]["observable_default_or_recommendation_bias"]["state"], "UNKNOWN")
        self.assertFalse(receipt["claims"]["external_endorsement_claimed"])
        self.assertFalse(receipt["claims"]["hugging_face_operated_interlock_claimed"])
        self.assertFalse(receipt["claims"]["certification_claimed"])
        self.assertFalse(receipt["claims"]["live_double_interlock_traversal_claimed"])

    def test_dashboard_is_static_receipt_derived_and_explicitly_not_live(self) -> None:
        admission = DEST.bind_fixture_intake(self.exchange)
        receipt = EVAL.evaluate(self.exchange, admission)
        page = DASH.render(self.exchange, receipt, 12)
        self.assertIn("FIXTURE / NOT LIVE-ADMITTED", page)
        self.assertIn(receipt["receipt_id"], page)
        self.assertIn("does not claim Hugging Face endorsement", page)
        self.assertNotIn("<script", page.lower())

    def test_profile_declares_twice_daily_public_target_without_runtime_authority(self) -> None:
        profile = json.loads((ROOT / "config/sv_dn1_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["public_dashboard"]["target_refresh_hours"], 12)
        self.assertTrue(profile["public_dashboard"]["static_receipt_derived"])
        self.assertFalse(profile["public_dashboard"]["javascript_required"])
        self.assertEqual(profile["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
