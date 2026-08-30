from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("svdn1_promote", ROOT / "scripts/promote_sv_dn1_public_result.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


def write_fixture(root: Path, *, publication_state: str = "PUBLIC_OBSERVED") -> None:
    pipeline = {
        "schema_version": "stegverse.sv-dn1.production-pipeline-observation/v1",
        "profile_id": "SV-DN-1",
        "observation_class": "LIVE",
        "publication_state": publication_state,
        "authority_effect": "NONE",
    }
    analysis = {
        "schema_version": "stegverse.sv-dn1.first-round-analysis/v1",
        "state": "ANALYZED",
        "profile_id": "SV-DN-1",
        "exchange_id": "sha256:" + "a" * 64,
        "manifest_receipt_id": "mr-1",
        "external_evaluation": {"result_receipt_id": "receipt-1"},
        "production_pipeline": pipeline,
        "artifacts": dict(MOD.EXPECTED_ANALYSIS_ARTIFACTS),
        "claims": {
            "first_round_analyzed": True,
            "dashboard_generated": True,
            "dashboard_publicly_hosted": False,
            "certification_claimed": False,
            "production_perfection_claimed": False,
        },
        "authority_effect": "NONE",
    }
    result_receipt = {
        "receipt_id": "receipt-1",
        "exchange_id": analysis["exchange_id"],
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "first-round-analysis.json").write_text(json.dumps(analysis, sort_keys=True) + "\n", encoding="utf-8")
    (root / "production-pipeline-observation.json").write_text(json.dumps(pipeline, sort_keys=True) + "\n", encoding="utf-8")
    (root / "result-receipt.json").write_text(json.dumps(result_receipt, sort_keys=True) + "\n", encoding="utf-8")
    (root / "report.md").write_text("# authentic report\n", encoding="utf-8")
    (root / "index.html").write_text("<!doctype html><title>SV-DN-1 authentic</title>\n", encoding="utf-8")


class SvDn1PublicPromotionTests(unittest.TestCase):
    def test_authentic_live_artifacts_promote_exact_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            finalized = base / "finalized"
            public = base / "public"
            receipt_path = base / "receipts/latest.json"
            write_fixture(finalized)
            result = MOD.promote(finalized, public, receipt_path)
            self.assertEqual(result["state"], "PROMOTION_READY_FOR_REPOSITORY_MUTATION")
            self.assertEqual(result["publication_state"], "PUBLIC_OBSERVED")
            self.assertTrue(result["exact_bytes_preserved"])
            self.assertFalse(result["semantic_rewrite_performed"])
            self.assertFalse(result["network_fetch_performed"])
            self.assertFalse(result["credential_used"])
            self.assertFalse(result["repository_writeback_performed"])
            self.assertFalse(result["deployment_performed"])
            self.assertEqual(result["authority_effect"], "NONE_STATIC_PROJECTION_ONLY")
            self.assertEqual(result["source_artifact_sha256"], result["destination_artifact_sha256"])
            for name in MOD.PROMOTED_FILES:
                self.assertEqual((finalized / name).read_bytes(), (public / name).read_bytes())
            self.assertTrue(receipt_path.is_file())

    def test_withheld_pipeline_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            finalized = Path(td) / "finalized"
            write_fixture(finalized, publication_state="WITHHELD")
            with self.assertRaisesRegex(ValueError, "publication state remains WITHHELD"):
                MOD.validate_finalized(finalized)

    def test_non_analyzed_input_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            finalized = Path(td) / "finalized"
            write_fixture(finalized)
            path = finalized / "first-round-analysis.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["state"] = "READY"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not ANALYZED"):
                MOD.validate_finalized(finalized)

    def test_exchange_identity_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            finalized = Path(td) / "finalized"
            write_fixture(finalized)
            path = finalized / "result-receipt.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["exchange_id"] = "sha256:" + "b" * 64
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exchange mismatch"):
                MOD.validate_finalized(finalized)

    def test_result_receipt_identity_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            finalized = Path(td) / "finalized"
            write_fixture(finalized)
            path = finalized / "result-receipt.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["receipt_id"] = "receipt-other"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "receipt identity mismatch"):
                MOD.validate_finalized(finalized)

    def test_unexpected_artifact_map_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            finalized = Path(td) / "finalized"
            write_fixture(finalized)
            path = finalized / "first-round-analysis.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["artifacts"]["dashboard"] = "other.html"
            path.write_text(json.dumps(value) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected finalized artifact map"):
                MOD.validate_finalized(finalized)


if __name__ == "__main__":
    unittest.main()
