from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load():
    path = ROOT / "scripts" / "validate_sv_dn1_runtime_source.py"
    spec = importlib.util.spec_from_file_location("sv_dn1_runtime_source_validator_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


V = load()


class SvDn1RuntimeSourcePinTests(unittest.TestCase):
    def test_current_pinned_source_validates(self) -> None:
        manifest = V.load_manifest(ROOT / "config" / "sv_dn1_runtime_source_manifest.json")
        result = V.validate_source(ROOT, manifest)
        self.assertEqual(result["state"], "PASS")
        self.assertEqual(result["missing_files"], [])
        self.assertEqual(result["mismatches"], [])
        self.assertGreaterEqual(len(result["verified_files"]), 10)

    def test_source_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target = root / "example.txt"
            target.write_text("changed\n", encoding="utf-8")
            manifest = {
                "schema":"stegverse.sv-dn1.runtime-source-manifest/v1",
                "hash_profile":"git-blob-sha1",
                "source_basis_commit":"test",
                "files":{"example.txt":"0"*40},
            }
            result = V.validate_source(root, manifest)
            self.assertEqual(result["state"], "FAIL")
            self.assertEqual(len(result["mismatches"]), 1)

    def test_missing_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            manifest = {
                "schema":"stegverse.sv-dn1.runtime-source-manifest/v1",
                "hash_profile":"git-blob-sha1",
                "source_basis_commit":"test",
                "files":{"missing.txt":"0"*40},
            }
            result = V.validate_source(Path(td), manifest)
            self.assertEqual(result["state"], "FAIL")
            self.assertEqual(result["missing_files"], ["missing.txt"])


if __name__ == "__main__":
    unittest.main()
