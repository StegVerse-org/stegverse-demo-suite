from __future__ import annotations

import copy
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


HF = load("sv_dn1_hf_self_eval_test", "scripts/sv_dn1_hf_interlock.py")
DEST = load("sv_dn1_dest_self_eval_test", "scripts/sv_dn1_stegverse_interlock.py")
EVAL = load("sv_dn1_eval_self_eval_test", "scripts/sv_dn1_evaluator.py")
PIPE = load("sv_dn1_pipeline_observation_test", "scripts/build_sv_dn1_production_pipeline_observation.py")
DASH = load("sv_dn1_dashboard_self_eval_test", "scripts/render_sv_dn1_dashboard.py")
REPORT = load("sv_dn1_report_self_eval_test", "scripts/render_sv_dn1_report.py")


class SvDn1ProductionSelfEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.native = json.loads((ROOT / "fixtures/sv_dn1/hf_model_baseline.json").read_text())
        self.exchange = HF.build_exchange(
            self.native,
            "https://huggingface.co/stegverse-fixture/example-open-model",
            "2026-08-27T12:00:00Z",
        )
        self.admission = DEST.bind_fixture_intake(self.exchange)
        self.receipt = EVAL.evaluate(self.exchange, self.admission)

    def test_public_readiness_explicitly_requires_bounded_confidence_not_perfection(self) -> None:
        policy = json.loads((ROOT / "config/sv_dn1_public_readiness.json").read_text())
        self.assertEqual(
            policy["governing_principle"],
            "PUBLIC_READINESS_REQUIRES_BOUNDED_OBSERVABLE_IMPERFECTION_NOT_PERFECTION",
        )
        self.assertTrue(policy["production_stack_is_subject_of_observation"])
        self.assertTrue(policy["production_status_does_not_imply_correctness"])
        self.assertTrue(policy["public_evaluation_may_expose_failures"])
        self.assertTrue(policy["public_evaluation_may_expose_unknowns"])
        self.assertTrue(policy["does_not_require"]["all_lanes_pass"])
        self.assertTrue(policy["does_not_require"]["zero_known_defects"])
        self.assertTrue(policy["does_not_require"]["zero_unknowns"])

    def test_fixture_never_promotes_production_lane_observation(self) -> None:
        pipeline = PIPE.build(self.exchange, self.receipt)
        self.assertEqual(pipeline["observation_class"], "FIXTURE")
        self.assertEqual(pipeline["publication_state"], "WITHHELD")
        self.assertEqual(pipeline["first_unresolved_pipeline_boundary"], "external_source_capture")
        for lane in pipeline["lanes"].values():
            self.assertIn(lane["state"], {"NOT_OBSERVED", "NOT_APPLICABLE"})
        self.assertFalse(pipeline["claims"]["production_perfection_claimed"])
        self.assertFalse(pipeline["claims"]["certification_claimed"])

    def test_fixture_rejects_explicit_production_pass(self) -> None:
        with self.assertRaises(ValueError):
            PIPE.build(
                self.exchange,
                self.receipt,
                {
                    "external_source_capture": {
                        "state": "PASS",
                        "evidence_refs": ["sha256:fixture"],
                        "known_errors": [],
                        "unknowns": [],
                        "authority_effect": "NONE",
                    }
                },
            )

    def test_live_pipeline_can_be_public_with_explicit_limitations(self) -> None:
        live = copy.deepcopy(self.receipt)
        live["sdk_intake"]["binding_state"] = "SDK_ADMITTED"
        evidence = {}
        for lane in PIPE.REQUIRED_LANES:
            evidence[lane] = {
                "state": "PASS",
                "evidence_refs": [f"receipt:{lane}"],
                "known_errors": [],
                "unknowns": [],
                "authority_effect": "NONE",
            }
        evidence["intr"] = {
            "state": "DEGRADED",
            "evidence_refs": ["receipt:intr"],
            "known_errors": ["latency exceeded target but lineage remained intact"],
            "unknowns": [],
            "authority_effect": "NONE",
        }
        pipeline = PIPE.build(self.exchange, live, evidence)
        self.assertEqual(pipeline["observation_class"], "LIVE")
        self.assertEqual(pipeline["publication_state"], "PUBLIC_WITH_LIMITATIONS")
        self.assertEqual(pipeline["first_unresolved_pipeline_boundary"], "intr")
        self.assertIn("intr: latency exceeded target but lineage remained intact", pipeline["known_errors"])
        self.assertFalse(pipeline["claims"]["all_lanes_pass"])
        self.assertFalse(pipeline["claims"]["production_perfection_claimed"])

    def test_unknown_is_publicly_representable_when_explicit(self) -> None:
        live = copy.deepcopy(self.receipt)
        live["sdk_intake"]["binding_state"] = "SDK_ADMITTED"
        evidence = {}
        for lane in PIPE.REQUIRED_LANES:
            evidence[lane] = {
                "state": "PASS",
                "evidence_refs": [f"receipt:{lane}"],
                "known_errors": [],
                "unknowns": [],
                "authority_effect": "NONE",
            }
        evidence["reconstruction"] = {
            "state": "UNKNOWN",
            "evidence_refs": ["receipt:reconstruction-attempt"],
            "known_errors": [],
            "unknowns": ["independent reconstruction has not completed"],
            "authority_effect": "NONE",
        }
        pipeline = PIPE.build(self.exchange, live, evidence)
        self.assertEqual(pipeline["publication_state"], "PUBLIC_WITH_LIMITATIONS")
        self.assertEqual(pipeline["lanes"]["reconstruction"]["state"], "UNKNOWN")
        self.assertFalse(pipeline["claims"]["zero_unknowns"])

    def test_not_observed_or_not_reached_withholds_public_result(self) -> None:
        live = copy.deepcopy(self.receipt)
        live["sdk_intake"]["binding_state"] = "SDK_ADMITTED"
        evidence = {
            lane: {
                "state": "PASS",
                "evidence_refs": [f"receipt:{lane}"],
                "known_errors": [],
                "unknowns": [],
                "authority_effect": "NONE",
            }
            for lane in PIPE.REQUIRED_LANES
        }
        evidence["master_records_custody"] = {
            "state": "NOT_REACHED",
            "evidence_refs": [],
            "known_errors": [],
            "unknowns": ["upstream execution stopped before custody"],
            "authority_effect": "NONE",
        }
        pipeline = PIPE.build(self.exchange, live, evidence)
        self.assertEqual(pipeline["publication_state"], "WITHHELD")
        self.assertEqual(pipeline["first_unresolved_pipeline_boundary"], "master_records_custody")

    def test_dashboard_and_report_make_production_self_evaluation_prominent(self) -> None:
        pipeline = PIPE.build(self.exchange, self.receipt)
        page = DASH.render(self.exchange, self.receipt, 12, pipeline)
        report = REPORT.render(self.exchange, self.receipt, pipeline)
        self.assertIn("StegVerse production pipeline under observation", page)
        self.assertIn("Public readiness does not require perfection", page)
        self.assertIn("First unresolved pipeline boundary", page)
        self.assertIn("StegVerse production pipeline under observation", report)
        self.assertIn("Public readiness is bounded confidence, not perfection", report)
        self.assertNotIn("<script", page.lower())


if __name__ == "__main__":
    unittest.main()
