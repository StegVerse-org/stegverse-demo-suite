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
    def test_profile_is_identity_neutral_and_sdk_mediated(self) -> None:
        profile = json.loads((ROOT / "config/evaluator_profile.json").read_text(encoding="utf-8"))
        self.assertEqual(profile["authority_effect"], "NONE")
        self.assertFalse(profile["recipient_specific"])
        self.assertTrue(profile["frozen_state_required"])
        self.assertTrue(profile["terms_acceptance_required"])
        self.assertEqual(profile["relationship_manager"], "StegVerse-org/StegVerse-SDK")
        self.assertFalse(profile["network_required_to_build"])
        self.assertFalse(profile["network_required_to_verify"])
        self.assertFalse(profile["github_actions_required"])
        self.assertFalse(profile["render_required"])
        self.assertEqual(profile["direct_external_stegverse_connections"], [])
        self.assertEqual(set(profile["sdk_mediated_routes"]), {
            "StegGhost/entity-sandbox-runner",
            "StegVerse-org/LLM-adapter:evaluator-entry",
        })
        self.assertFalse(profile["llm_adapter_direct_access"])

    def test_catalog_exposes_llm_only_through_sdk_relationship(self) -> None:
        catalog = json.loads((ROOT / "config/evaluator_capability_catalog.json").read_text(encoding="utf-8"))
        self.assertTrue(catalog["frozen_catalog"])
        self.assertTrue(catalog["terms_acceptance_required"])
        self.assertEqual(catalog["relationship_manager"], "StegVerse-org/StegVerse-SDK")
        llm = next(c for c in catalog["capabilities"] if c["capability_id"] == "llm_adapter.evaluator_interaction")
        self.assertFalse(llm["direct_access"])
        self.assertTrue(llm["relationship_required"])
        self.assertTrue(llm["terms_acceptance_required"])
        self.assertFalse(llm["provider_credentials_exposed"])
        self.assertFalse(llm["sovereign_adapter_authority_exposed"])

    def test_license_manifest_separates_license_from_service_relationship(self) -> None:
        licenses = json.loads((ROOT / "config/evaluator_license_manifest.json").read_text(encoding="utf-8"))
        self.assertTrue(licenses["license_and_service_relationship_are_separate"])
        self.assertEqual({c["repository"] for c in licenses["components"]}, {
            "StegVerse-org/stegverse-demo-suite",
            "StegVerse-org/StegVerse-SDK",
            "StegVerse-org/LLM-adapter",
        })
        self.assertTrue(all(c["license_id"] == "MIT" for c in licenses["components"]))

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
