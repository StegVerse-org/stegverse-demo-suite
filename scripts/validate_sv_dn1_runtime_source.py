#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "config" / "sv_dn1_runtime_source_manifest.json"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def load_manifest(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("runtime source manifest must be an object")
    if value.get("schema") != "stegverse.sv-dn1.runtime-source-manifest/v1":
        raise ValueError("wrong runtime source manifest schema")
    if value.get("hash_profile") != "git-blob-sha1":
        raise ValueError("unsupported runtime source hash profile")
    files = value.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("runtime source manifest files missing")
    return value


def validate_source(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    mismatches: list[dict[str, str]] = []
    missing: list[str] = []
    verified: list[str] = []
    for rel, expected in sorted(manifest["files"].items()):
        path = root / rel
        if not path.is_file():
            missing.append(rel)
            continue
        actual = git_blob_sha1(path.read_bytes())
        if actual != expected:
            mismatches.append({"path": rel, "expected": str(expected), "actual": actual})
        else:
            verified.append(rel)
    state = "PASS" if not missing and not mismatches else "FAIL"
    return {
        "schema":"stegverse.sv-dn1.runtime-source-validation/v1",
        "state":state,
        "source_basis_commit":manifest.get("source_basis_commit"),
        "hash_profile":"git-blob-sha1",
        "verified_files":verified,
        "missing_files":missing,
        "mismatches":mismatches,
        "authority_effect":"NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = ap.parse_args()
    manifest = load_manifest(Path(args.manifest))
    result = validate_source(Path(args.root), manifest)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
