#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "config" / "evaluator_profile.json"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def blocked(path: Path, profile: dict) -> bool:
    names = {part.lower() for part in path.parts}
    if any(name.lower() in names for name in profile["excluded_path_names"]):
        return True
    lowered = path.name.lower()
    return any(fragment.lower() in lowered for fragment in profile["prohibited_filename_fragments"])


def copy_entry(src: Path, dst: Path, profile: dict) -> None:
    if blocked(src.relative_to(ROOT), profile):
        return
    if src.is_file():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return
    if src.is_dir():
        for child in sorted(src.rglob("*")):
            rel = child.relative_to(ROOT)
            if child.is_file() and not blocked(rel, profile):
                target = dst / child.relative_to(src)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(child, target)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--source-revision", required=True)
    args = ap.parse_args()
    source_revision = args.source_revision.strip()
    if len(source_revision) < 7 or any(ch.isspace() for ch in source_revision):
        raise SystemExit("EVALUATOR_BUILD_FAIL: invalid source revision")
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    out = Path(args.output).resolve()
    if out == ROOT:
        raise SystemExit("EVALUATOR_BUILD_FAIL: output cannot be repository root")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    copied_sources: list[str] = []
    for entry in profile["included_roots"]:
        src = ROOT / entry
        if not src.exists():
            continue
        copy_entry(src, out / entry, profile)
        copied_sources.append(entry)
    payload_name = profile["optional_frozen_payload_root"]
    payload = ROOT / payload_name
    if payload.exists():
        copy_entry(payload, out / payload_name, profile)
        copied_sources.append(payload_name)
    shutil.copy2(PROFILE, out / "evaluator_profile.json")
    readme = f"""# StegVerse General Portable Evaluator Bundle\n\nProfile: `{profile['profile_id']}`\nFrozen source revision: `{source_revision}`\n\nThis is an identity-neutral, non-authority-bearing frozen evaluation/development package. It remains inspectable and locally verifiable without GitHub Actions, Render, or a live StegVerse runtime.\n\nInteractive StegVerse access is never direct from the bundle. A participant must first accept the current Demo TOS/TOU and establish an SDK evaluation relationship. The SDK may then admit a bounded StegGhost sandbox route or the restricted LLM-adapter evaluator entry.\n\nDirect LLM-adapter access is prohibited. No package capability grants production activation, heartbeat, governance, wallet, broadcast, custody, provider-credential, TV/TVC capability, private-repository, or sovereign-runtime authority.\n\nLicensing is declared per component in `config/evaluator_license_manifest.json`. Software-license rights and Demo service/SDK relationship scope are separate.\n"""
    (out / profile["bundle_readme"]).write_text(readme, encoding="utf-8")
    files = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != profile["bundle_manifest"]:
            rel = path.relative_to(out).as_posix()
            files.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})
    manifest = {
        "schema": "stegverse.demo-evaluator-manifest.v2",
        "profile_id": profile["profile_id"],
        "recipient_specific": False,
        "frozen_state": True,
        "source_revision": source_revision,
        "authority_effect": "NONE",
        "terms_acceptance_required_for_connection": True,
        "relationship_manager": profile["relationship_manager"],
        "network_required_to_build": False,
        "network_required_to_verify": False,
        "github_actions_required": False,
        "render_required": False,
        "direct_external_stegverse_connections": [],
        "sdk_mediated_routes": profile["sdk_mediated_routes"],
        "llm_adapter_direct_access": False,
        "capability_catalog": profile["capability_catalog"],
        "license_manifest": profile["license_manifest"],
        "copied_sources": copied_sources,
        "file_count": len(files),
        "files": files,
    }
    (out / profile["bundle_manifest"]).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": "EVALUATOR_BUNDLE_BUILT", "output": str(out), "source_revision": source_revision, "file_count": len(files)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
