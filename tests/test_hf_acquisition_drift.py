import importlib.util
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "scripts" / "analyze_hf_acquisition_drift.py"
spec = importlib.util.spec_from_file_location("hf_drift", P)
MOD = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MOD)

class HuggingFaceAcquisitionDriftTests(unittest.TestCase):
    def test_inference_only_is_insufficient(self):
        r = MOD.classify([{"evidence_class":"INFERENCE","direction":"NEGATIVE","confidence":1.0}])
        self.assertEqual(r["state"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(r["inference_promoted_to_observation"])

    def test_negative_direct_evidence(self):
        r = MOD.classify([{"evidence_class":"RECEIPT_BOUND_SV_DN1_OBSERVATION","direction":"NEGATIVE","confidence":0.9}])
        self.assertEqual(r["state"], "COMMUNITY_NEGATIVE_DRIFT")

    def test_conflicting_evidence_is_mixed(self):
        r = MOD.classify([
            {"evidence_class":"DIRECT_PUBLIC_OBSERVATION","direction":"NEGATIVE","confidence":0.9},
            {"evidence_class":"OFFICIAL_ANNOUNCEMENT","direction":"POSITIVE","confidence":0.8},
        ])
        self.assertEqual(r["state"], "MIXED_DRIFT")

if __name__ == "__main__":
    unittest.main()
