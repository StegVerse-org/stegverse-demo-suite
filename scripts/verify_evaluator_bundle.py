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
    if manifest.get("schema") != "stegverse.demo-evaluator-manifest.v1":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: manifest schema")
    if manifest.get("profile_id") != profile.get("profile_id"):
        raise SystemExit("EVALUATOR_VERIFY_FAIL: profile mismatch")
    if manifest.get("authority_effect") != "NONE":
        raise SystemExit("EVALUATOR_VERIFY_FAIL: authority effect")
    for key in ("network_required_to_build", "network_required_to_verify", "github_actions_required", "render_required"):
        if manifest.get(key) is not False:
            raise SystemExit(f"EVALUATOR_VERIFY_FAIL: {key}")
    if manifest.get("allowed_external_stegverse_connections") != ["StegGhost/entity-sandbox-runner"]:
        raise SystemExit("EVALUATOR_VERIFY_FAIL: external connection boundary")
    if "StegVerse-org/LLM-adapter" not in manifest.get("excluded_repositories", []):
        raise SystemExit("EVALUATOR_VERIFY_FAIL: LLM-adapter exclusion missing")

    expected = {item["path"]: item for item in manifest.get("files", [])}
    actual = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "EVALUATOR_MANIFEST.json":
            continue
        rel = path.relative_to(root).as_posix()
        actual[rel] = {"sha256": sha256(path), "size": path.stat().st_size}
    if set(actual) != set(expected):
        missing = sorted(set(expected) - set(actual))
        extra = sorted(set(actual) - set(expected))
        raise SystemExit(f"EVALUATOR_VERIFY_FAIL: manifest file set drift missing={missing} extra={extra}")
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

    print(json.dumps({"state": "EVALUATOR_BUNDLE_VERIFIED", "file_count": len(actual), "authority_effect": "NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
