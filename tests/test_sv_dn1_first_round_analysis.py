from __future__ import annotations

import copy
import importlib.util
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


BASE = load("sv_dn1_live_binding_fixture_for_first_round", "tests/test_sv_dn1_live_sdk_result_binding.py")
FINAL = load("sv_dn1_first_round_finalizer_test", "scripts/finalize_sv_dn1_first_round.py")
BIND = load("sv_dn1_first_round_binder_test", "scripts/bind_sv_dn1_sdk_live_result.py")
EVAL = load("sv_dn1_first_round_evaluator_test", "scripts/sv_dn1_evaluator.py")
DASH = load("sv_dn1_first_round_dashboard_test", "scripts/render_sv_dn1_dashboard.py")


class SvDn1FirstRoundAnalysisTests(unittest.TestCase):
    def setUp(self) -> None:
        fixture = BASE.SvDn1LiveSdkResultBindingTests(methodName="test_binds_exact_canonical_sdk_result_to_sdk_admitted_evaluator_input")
        fixture.setUp()
        self.capture = fixture.capture
        self.exchange = fixture.exchange
        self.intr = fixture.intr
        self.packet = fixture.packet
        self.sdk_result = fixture.sdk_result
        self.admission = BIND.bind(self.packet, self.sdk_result)
        self.result_receipt = EVAL.evaluate(self.exchange, self.admission)
        self.reconstruction = {
            "schema": "stegverse.public-inspection-reconstruction.v2",
            "operation_id": "OP-RECONSTRUCT-SYNTHETIC",
            "manifest_receipt_id": self.admission["sdk_intake"]["intake_receipt_id"],
            "transaction_id": self.admission["route"]["transaction_id"],
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "operation_transition_custody_status": "RECORDED",
            "operation_receipt_ids": ["MR-OP-SYNTHETIC-1", "MR-OP-SYNTHETIC-2"],
        }

    def finalize(self, *, findings=None, reconstruction=None, replay=None):
        return FINAL.finalize(
            capture=copy.deepcopy(self.capture),
            exchange=copy.deepcopy(self.exchange),
            intr=copy.deepcopy(self.intr),
            candidate=copy.deepcopy(self.packet),
            sdk_result=copy.deepcopy(self.sdk_result),
            admission=copy.deepcopy(self.admission),
            result_receipt=copy.deepcopy(self.result_receipt),
            reconstruction=copy.deepcopy(reconstruction or self.reconstruction),
            replay=copy.deepcopy(replay),
            lane_findings=copy.deepcopy(findings),
        )

    def test_first_round_is_analyzed_when_exact_production_evidence_reconstructs(self) -> None:
        analysis, pipeline = self.finalize()
        self.assertEqual(analysis["state"], "ANALYZED")
        self.assertEqual(pipeline["observation_class"], "LIVE")
        self.assertEqual(pipeline["publication_state"], "PUBLIC_OBSERVED")
        self.assertTrue(analysis["claims"]["first_round_analyzed"])
        self.assertTrue(analysis["claims"]["dashboard_generated"])
        self.assertFalse(analysis["claims"]["dashboard_publicly_hosted"])
        self.assertGreater(len(analysis["external_evaluation"]["unknowns"]), 0)

    def test_known_pipeline_defect_is_public_with_limitations_not_hidden(self) -> None:
        analysis, pipeline = self.finalize(findings={
            "intr": {
                "state": "DEGRADED",
                "known_errors": ["latency exceeded declared observation target while receipt lineage remained intact"],
                "unknowns": [],
                "evidence_refs": ["metric:intr-latency-synthetic"],
            }
        })
        self.assertEqual(pipeline["publication_state"], "PUBLIC_WITH_LIMITATIONS")
        self.assertEqual(pipeline["first_unresolved_pipeline_boundary"], "intr")
        self.assertIn("intr: latency exceeded declared observation target while receipt lineage remained intact", pipeline["known_errors"])
        self.assertTrue(analysis["claims"]["first_round_analyzed"])

    def test_explicit_pipeline_unknown_is_public_with_limitations(self) -> None:
        _, pipeline = self.finalize(findings={
            "public_projection": {
                "state": "UNKNOWN",
                "known_errors": [],
                "unknowns": ["independent public HTTPS observation has not completed"],
                "evidence_refs": ["artifact:index.html"],
            }
        })
        self.assertEqual(pipeline["publication_state"], "PUBLIC_WITH_LIMITATIONS")
        self.assertFalse(pipeline["claims"]["zero_unknowns"])

    def test_reconstruction_identity_mismatch_fails_closed(self) -> None:
        bad = copy.deepcopy(self.reconstruction)
        bad["transaction_id"] = "TX-WRONG"
        with self.assertRaises(ValueError):
            self.finalize(reconstruction=bad)

    def test_reconstruction_consequence_reexecution_fails_closed(self) -> None:
        bad = copy.deepcopy(self.reconstruction)
        bad["consequence_reexecuted"] = True
        with self.assertRaises(ValueError):
            self.finalize(reconstruction=bad)

    def test_tampered_evaluator_receipt_fails_closed(self) -> None:
        bad_receipt = copy.deepcopy(self.result_receipt)
        bad_receipt["summary"]["pass"] += 1
        with self.assertRaises(ValueError):
            FINAL.finalize(
                capture=self.capture,
                exchange=self.exchange,
                intr=self.intr,
                candidate=self.packet,
                sdk_result=self.sdk_result,
                admission=self.admission,
                result_receipt=bad_receipt,
                reconstruction=self.reconstruction,
            )

    def test_replay_is_bound_when_supplied(self) -> None:
        replay = {
            "manifest_receipt_id": self.admission["sdk_intake"]["intake_receipt_id"],
            "deterministic_disposition_match": True,
            "candidate_identity_match": True,
            "consequence_reexecuted": False,
            "original_record_mutated": False,
            "operation_transition_custody_status": "RECORDED",
        }
        analysis, _ = self.finalize(replay=replay)
        self.assertTrue(analysis["replay"]["deterministic_disposition_match"])

    def test_dashboard_exposes_same_pipeline_state(self) -> None:
        _, pipeline = self.finalize()
        page = DASH.render(self.exchange, self.result_receipt, 12, pipeline)
        self.assertIn("StegVerse production pipeline under observation", page)
        self.assertIn("PUBLIC_OBSERVED", page)
        self.assertIn("First unresolved pipeline boundary:", page)
        self.assertNotIn("<script", page.lower())


if __name__ == "__main__":
    unittest.main()
