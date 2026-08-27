#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def entry(exchange: dict, receipt: dict) -> dict:
    return {
        "observed_at": exchange["source_object"]["observed_at"],
        "native_id": exchange["source_object"]["native_id"],
        "native_revision": exchange["source_object"]["native_revision"],
        "exchange_id": exchange["exchange_id"],
        "receipt_id": receipt["receipt_id"],
        "mapping_profile": exchange["semantic_mapping"]["profile"],
        "ruleset_hash": exchange["semantic_mapping"]["ruleset_hash"],
        "sdk_binding": receipt["sdk_intake"]["binding_state"],
        "summary": receipt["summary"],
        "dimensions": {k: v["state"] for k, v in receipt["dimensions"].items()},
        "authority_effect": receipt["authority_effect"],
    }


def build_history(observation_dirs: list[Path]) -> dict:
    entries = []
    for directory in observation_dirs:
        exchange_path = directory / "exchange.json"
        receipt_path = directory / "result-receipt.json"
        if not exchange_path.exists() or not receipt_path.exists():
            continue
        exchange = json.loads(exchange_path.read_text(encoding="utf-8"))
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        entries.append(entry(exchange, receipt))
    entries.sort(key=lambda x: (x["observed_at"], x["receipt_id"]))
    for i, current in enumerate(entries):
        if i == 0:
            current["delta_from_previous"] = None
            continue
        previous = entries[i - 1]
        dimension_changes = {
            key: {"from": previous["dimensions"].get(key), "to": value}
            for key, value in current["dimensions"].items()
            if previous["dimensions"].get(key) != value
        }
        current["delta_from_previous"] = {
            "revision_changed": current["native_revision"] != previous["native_revision"],
            "ruleset_changed": current["ruleset_hash"] != previous["ruleset_hash"],
            "sdk_binding_changed": current["sdk_binding"] != previous["sdk_binding"],
            "dimension_changes": dimension_changes,
        }
    return {
        "schema_version": "stegverse.sv-dn1.dashboard-history/v1",
        "observation_count": len(entries),
        "latest_receipt_id": entries[-1]["receipt_id"] if entries else None,
        "entries": entries,
        "authority_effect": "NONE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--observations-root", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    root = Path(args.observations_root)
    dirs = sorted([p for p in root.iterdir() if p.is_dir()]) if root.exists() else []
    history = build_history(dirs)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(history, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_DASHBOARD_HISTORY_BUILT",
        "observation_count": history["observation_count"],
        "latest_receipt_id": history["latest_receipt_id"],
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
