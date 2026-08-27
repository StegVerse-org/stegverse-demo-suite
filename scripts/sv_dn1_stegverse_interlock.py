#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def validate_exchange(exchange: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if exchange.get("schema_version") != "stegverse.sv-dn1.interlock-exchange/v1":
        blockers.append("wrong_schema_version")
    if exchange.get("source_system") != "huggingface":
        blockers.append("wrong_source_system")
    far = exchange.get("far_side_receipt", {})
    intr = exchange.get("intr", {})
    if far.get("interlock_role") != "SOURCE_SEMANTIC_ADAPTER":
        blockers.append("wrong_far_side_role")
    if far.get("authority_effect") != "NONE" or intr.get("authority_effect") != "NONE":
        blockers.append("authority_effect_forbidden")
    if intr.get("previous_receipt_hash") != far.get("transformation_hash"):
        blockers.append("intr_receipt_chain_mismatch")

    raw = exchange.get("raw_evidence", {})
    native = raw.get("preserved_native_fields")
    if not isinstance(native, dict):
        blockers.append("native_evidence_missing")
    elif digest(native) != raw.get("source_sha256"):
        blockers.append("native_source_hash_mismatch")

    mapping = exchange.get("semantic_mapping", {})
    if mapping.get("profile") != "SV-DN-1-HF/v1":
        blockers.append("wrong_mapping_profile")
    for tx in mapping.get("lossy_transformations", []):
        if not tx.get("native_preserved"):
            blockers.append("silent_loss_forbidden")

    expected_tx = digest({
        "exchange_id": exchange.get("exchange_id"),
        "semantic": exchange.get("semantic", {}),
        "transformations": mapping.get("transformations", []),
        "lossy_transformations": mapping.get("lossy_transformations", []),
        "source_sha256": raw.get("source_sha256"),
    })
    if expected_tx != far.get("transformation_hash"):
        blockers.append("transformation_hash_mismatch")
    return sorted(set(blockers))


def bind_fixture_intake(exchange: dict[str, Any]) -> dict[str, Any]:
    blockers = validate_exchange(exchange)
    if blockers:
        return {"state": "REJECTED", "blockers": blockers, "authority_effect": "NONE"}
    manifest_hash = digest({
        "exchange_id": exchange["exchange_id"],
        "source_sha256": exchange["raw_evidence"]["source_sha256"],
        "mapping_hash": exchange["semantic_mapping"]["ruleset_hash"],
    })
    return {
        "state": "ADMITTED_FOR_FIXTURE_EVALUATION",
        "blockers": [],
        "exchange_id": exchange["exchange_id"],
        "sdk_intake": {
            "manifest_hash": manifest_hash,
            "intake_receipt_id": digest({"manifest_hash": manifest_hash, "route": "SV-DN-1"}),
            "binding_state": "FIXTURE_BOUND",
        },
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    result = bind_fixture_intake(exchange)
    Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] != "REJECTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
