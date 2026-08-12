#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("bundle")
    args = ap.parse_args()
    root = Path(args.bundle).resolve()
    manifest_path = root / "EVALUATOR_MANIFEST.json"
    profile_path = root / "evaluator_profile.json"
    if not manifest_path.is_file() or not profile_path.is_file():
        raise SystemExit("EVALUATOR_VERIFY_FAIL: manifest/profile missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "stegverse.demo-evaluator-manifest.v2":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: manifest schema")
    if manifest.get("profile_id") != profile.get("profile_id"):
        raise SystemExit("EVALUATOR_VERIFY_FAIL: profile mismatch")
    if manifest.get("recipient_specific") is not False or manifest.get("frozen_state") is not True:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: package identity/frozen state")
    if manifest.get("authority_effect") != "NONE":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: authority effect")
    for key in ("network_required_to_build", "network_required_to_verify", "github_actions_required", "render_required"):
        if manifest.get(key) is not False:
            raise SystemExit(f"EVALUATOR_VERIFY_FAIL: {key}")
    if manifest.get("terms_acceptance_required_for_connection") is not True:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: terms gate")
    if manifest.get("relationship_manager") != "StegVerse-org/StegVerse-SDK":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: relationship manager")
    if manifest.get("direct_external_stegverse_connections") != []:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: direct StegVerse connection")
    if manifest.get("llm_adapter_direct_access") is not False:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: direct LLM-adapter access")
    required_routes = {"StegGhost/entity-sandbox-runner", "StegVerse-org/LLM-adapter:evaluator-entry"}
    if set(manifest.get("sdk_mediated_routes") or []) != required_routes:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: SDK-mediated route boundary")
    catalog_rel = manifest.get("capability_catalog")
    licenses_rel = manifest.get("license_manifest")
    if not isinstance(catalog_rel, str) or not (root / catalog_rel).is_file():
        raise SystemExit("EVALUATOR_VERIFY_FAIL: capability catalog")
    if not isinstance(licenses_rel, str) or not (root / licenses_rel).is_file():
        raise SystemExit("EVALUATOR_VERIFY_FAIL: license manifest")
    catalog = json.loads((root / catalog_rel).read_text(encoding="utf-8"))
    if catalog.get("terms_acceptance_required") is not True or catalog.get("relationship_manager") != "StegVerse-org/StegVerse-SDK":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: catalog relationship contract")
    llm = next((c for c in catalog.get("capabilities", []) if c.get("capability_id") == "llm_adapter.evaluator_interaction"), None)
    if not llm or llm.get("direct_access") is not False or llm.get("relationship_required") is not True:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: LLM evaluator boundary")
    licenses = json.loads((root / licenses_rel).read_text(encoding="utf-8"))
    if licenses.get("license_and_service_relationship_are_separate") is not True or not licenses.get("components"):
        raise SystemExit("EVALUATOR_VERIFY_FAIL: licensing boundary")
    expected = {item["path"]: item for item in manifest.get("files", [])}
    actual = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "EVALUATOR_MANIFEST.json":
            continue
        rel = path.relative_to(root).as_posix()
        actual[rel] = {"sha256": sha256(path), "size": path.stat().st_size}
    if set(actual) != set(expected):
        raise SystemExit("EVALUATOR_VERIFY_FAIL: manifest file set drift")
    for rel, observed in actual.items():
        record = expected[rel]
        if observed["sha256"] != record.get("sha256") or observed["size"] != record.get("size"):
            raise SystemExit(f"EVALUATOR_VERIFY_FAIL: file drift {rel}")
    forbidden_names = {name.lower() for name in profile.get("excluded_path_names", [])}
    fragments = [v.lower() for v in profile.get("prohibited_filename_fragments", [])]
    for rel in actual:
        parts = {part.lower() for part in Path(rel).parts}
        if parts & forbidden_names:
            raise SystemExit(f"EVALUATOR_VERIFY_FAIL: excluded path included {rel}")
        name = Path(rel).name.lower()
        if any(fragment in name for fragment in fragments):
            raise SystemExit(f"EVALUATOR_VERIFY_FAIL: prohibited filename included {rel}")
    print(json.dumps({"state": "EVALUATOR_BUNDLE_VERIFIED", "source_revision": manifest["source_revision"], "file_count": len(actual), "authority_effect": "NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
