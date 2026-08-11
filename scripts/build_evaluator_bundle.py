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
    args = ap.parse_args()

    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    out = Path(args.output).resolve()
    if out == ROOT or ROOT in out.parents and out.name not in {"dist", "mansoor-evaluation"}:
        pass
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

    payload_name = profile["optional_evaluation_payload_root"]
    payload = ROOT / payload_name
    if payload.exists():
        copy_entry(payload, out / payload_name, profile)
        copied_sources.append(payload_name)

    shutil.copy2(PROFILE, out / "evaluator_profile.json")

    readme = f"""# StegVerse Portable Evaluator Bundle\n\nProfile: `{profile['profile_id']}`\n\nThis bundle is a non-authority-bearing evaluation and public-demo package. It can be copied and inspected without GitHub Actions, Render, or any hosted StegVerse runtime.\n\nPermitted external StegVerse sandbox connection: `StegGhost/entity-sandbox-runner` only.\n\nExplicitly excluded: `StegVerse-org/LLM-adapter`.\n\nThe package grants no production activation, heartbeat, governance, wallet, broadcast, custody, provider-credential, TV/TVC capability, or private-repository authority.\n\nUse `python scripts/verify_evaluator_bundle.py <bundle>` from a source checkout, or independently verify every SHA-256 listed in `EVALUATOR_MANIFEST.json`.\n"""
    (out / profile["bundle_readme"]).write_text(readme, encoding="utf-8")

    files = []
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name != profile["bundle_manifest"]:
            rel = path.relative_to(out).as_posix()
            files.append({"path": rel, "sha256": sha256(path), "size": path.stat().st_size})

    manifest = {
        "schema": "stegverse.demo-evaluator-manifest.v1",
        "profile_id": profile["profile_id"],
        "authority_effect": "NONE",
        "network_required_to_build": False,
        "network_required_to_verify": False,
        "github_actions_required": False,
        "render_required": False,
        "allowed_external_stegverse_connections": profile["allowed_external_stegverse_connections"],
        "excluded_repositories": profile["excluded_repositories"],
        "copied_sources": copied_sources,
        "file_count": len(files),
        "files": files,
    }
    manifest_path = out / profile["bundle_manifest"]
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": "EVALUATOR_BUNDLE_BUILT", "output": str(out), "file_count": len(files)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
