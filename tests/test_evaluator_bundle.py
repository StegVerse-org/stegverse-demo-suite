from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvaluatorBoundaryTests(unittest.TestCase):
    def test_profile_is_non_authorizing_and_stegghost_only(self) -> None:
        profile = json.loads((ROOT / "config/evaluator_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["authority_effect"], "NONE")
        self.assertFalse(profile["network_required_to_build"])
        self.assertFalse(profile["network_required_to_verify"])
        self.assertFalse(profile["github_actions_required"])
        self.assertFalse(profile["render_required"])
        self.assertEqual(profile["allowed_external_stegverse_connections"], ["StegGhost/entity-sandbox-runner"])
        self.assertIn("StegVerse-org/LLM-adapter", profile["excluded_repositories"])

    def test_profile_excludes_control_and_secret_surfaces(self) -> None:
        profile = json.loads((ROOT / "config/evaluator_profile.json").read_text(encoding="utf-8"))
        excluded = set(profile["excluded_path_names"])
        for required in (".git", ".github", ".stegverse_runtime", "runtime-secrets", "secrets", ".env"):
            self.assertIn(required, excluded)
        prohibited = set(profile["prohibited_authority"])
        for required in ("heartbeat_control", "wallet_signing", "transaction_broadcast", "provider_credential_access", "TV/TVC capability material"):
            self.assertIn(required, prohibited)

    def test_builder_and_verifier_are_standard_library_only(self) -> None:
        for rel in ("scripts/build_evaluator_bundle.py", "scripts/verify_evaluator_bundle.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for forbidden in ("requests", "urllib.request", "subprocess", "socket", "actions/checkout", "GITHUB_TOKEN", "RENDER_"):
                self.assertNotIn(forbidden, text)

    def test_builder_blocks_secret_like_paths(self) -> None:
        builder = load_module("evaluator_builder", ROOT / "scripts/build_evaluator_bundle.py")
        profile = json.loads((ROOT / "config/evaluator_profile.json").read_text(encoding="utf-8"))
        self.assertTrue(builder.blocked(Path("runtime-secrets/provider_0x"), profile))
        self.assertTrue(builder.blocked(Path("docs/private_key_notes.txt"), profile))
        self.assertTrue(builder.blocked(Path(".github/workflows/run.yml"), profile))
        self.assertFalse(builder.blocked(Path("docs/public_demo.md"), profile))


if __name__ == "__main__":
    unittest.main()
