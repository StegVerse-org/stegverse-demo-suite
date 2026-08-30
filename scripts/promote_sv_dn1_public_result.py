#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
from typing import Any, Mapping

EXPECTED_ANALYSIS_ARTIFACTS = {
    "result_receipt": "result-receipt.json",
    "production_pipeline_observation": "production-pipeline-observation.json",
    "report": "report.md",
    "dashboard": "index.html",
}
PROMOTED_FILES = (
    "first-round-analysis.json",
    "production-pipeline-observation.json",
    "result-receipt.json",
    "report.md",
    "index.html",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_object(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_finalized(finalized_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    analysis = load_object(finalized_dir / "first-round-analysis.json")
    pipeline = load_object(finalized_dir / "production-pipeline-observation.json")
    receipt = load_object(finalized_dir / "result-receipt.json")

    require(analysis.get("schema_version") == "stegverse.sv-dn1.first-round-analysis/v1", "wrong first-round analysis schema")
    require(analysis.get("state") == "ANALYZED", "first-round result is not ANALYZED")
    require(analysis.get("profile_id") == "SV-DN-1", "wrong profile id")
    require(analysis.get("authority_effect") == "NONE", "analysis authority effect must remain NONE")
    claims = analysis.get("claims") or {}
    require(claims.get("first_round_analyzed") is True, "first_round_analyzed claim missing")
    require(claims.get("dashboard_generated") is True, "dashboard_generated claim missing")
    require(claims.get("dashboard_publicly_hosted") is False, "input must not pre-claim public hosting")
    require(claims.get("certification_claimed") is False, "certification claim forbidden")
    require(claims.get("production_perfection_claimed") is False, "production perfection claim forbidden")
    require(analysis.get("artifacts") == EXPECTED_ANALYSIS_ARTIFACTS, "unexpected finalized artifact map")

    require(pipeline.get("schema_version") == "stegverse.sv-dn1.production-pipeline-observation/v1", "wrong production pipeline schema")
    require(pipeline.get("profile_id") == "SV-DN-1", "pipeline profile mismatch")
    require(pipeline.get("observation_class") == "LIVE", "public promotion requires LIVE observation class")
    require(pipeline.get("publication_state") in {"PUBLIC_OBSERVED", "PUBLIC_WITH_LIMITATIONS"}, "publication state remains WITHHELD or invalid")
    require(pipeline.get("authority_effect") == "NONE", "pipeline authority effect must remain NONE")
    require(analysis.get("production_pipeline") == pipeline, "analysis/pipeline object mismatch")

    exchange_id = analysis.get("exchange_id")
    require(isinstance(exchange_id, str) and exchange_id, "analysis exchange_id missing")
    require(receipt.get("exchange_id") == exchange_id, "analysis/result receipt exchange mismatch")
    result_receipt_id = (analysis.get("external_evaluation") or {}).get("result_receipt_id")
    require(isinstance(result_receipt_id, str) and result_receipt_id, "analysis result receipt id missing")
    require(receipt.get("receipt_id") == result_receipt_id, "analysis/result receipt identity mismatch")

    for name in PROMOTED_FILES:
        require((finalized_dir / name).is_file(), f"missing finalized artifact: {name}")
    return analysis, pipeline, receipt


def promote(finalized_dir: Path, public_dir: Path, receipt_path: Path) -> dict[str, Any]:
    source = finalized_dir.expanduser().resolve()
    destination = public_dir.expanduser().resolve()
    analysis, pipeline, _receipt = validate_finalized(source)

    source_hashes = {name: sha256_file(source / name) for name in PROMOTED_FILES}
    destination.mkdir(parents=True, exist_ok=True)
    for name in PROMOTED_FILES:
        shutil.copyfile(source / name, destination / name)
    destination_hashes = {name: sha256_file(destination / name) for name in PROMOTED_FILES}
    require(source_hashes == destination_hashes, "public promotion changed finalized artifact bytes")

    result = {
        "schema": "stegverse.sv-dn1.public-promotion-receipt/v1",
        "state": "PROMOTION_READY_FOR_REPOSITORY_MUTATION",
        "profile_id": "SV-DN-1",
        "exchange_id": analysis["exchange_id"],
        "manifest_receipt_id": analysis["manifest_receipt_id"],
        "publication_state": pipeline["publication_state"],
        "observation_class": pipeline["observation_class"],
        "source_artifact_sha256": source_hashes,
        "destination_artifact_sha256": destination_hashes,
        "exact_bytes_preserved": True,
        "semantic_rewrite_performed": False,
        "network_fetch_performed": False,
        "credential_used": False,
        "repository_writeback_performed": False,
        "deployment_performed": False,
        "certification_claimed": False,
        "authority_effect": "NONE_STATIC_PROJECTION_ONLY",
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    temp = receipt_path.with_name("." + receipt_path.name + ".tmp")
    temp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temp, receipt_path)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="Promote an already-finalized authentic SV-DN-1 result into the static public projection.")
    ap.add_argument("--finalized-dir", required=True, type=Path)
    ap.add_argument("--public-dir", type=Path, default=Path("public/sv-dn1"))
    ap.add_argument("--receipt", type=Path, default=Path("receipts/sv-dn1-public-promotion.latest.json"))
    args = ap.parse_args()
    result = promote(args.finalized_dir, args.public_dir, args.receipt)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
