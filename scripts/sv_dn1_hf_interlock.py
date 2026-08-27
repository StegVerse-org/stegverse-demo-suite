#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "config" / "sv_dn1_hf_mapping.v1.json"


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def get_path(obj: dict[str, Any], dotted: str) -> Any:
    cur: Any = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def set_path(obj: dict[str, Any], dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def project(rule: dict[str, Any], native: dict[str, Any]) -> tuple[bool, Any]:
    source = rule["source"][0]
    value = get_path(native, source)
    if value is None:
        return False, None
    op = rule["operation"]
    if op in ("copy", "copy_if_present"):
        return True, value
    if op == "copy_sorted":
        if not isinstance(value, list):
            raise ValueError(f"{rule['rule_id']}: expected list")
        return True, sorted(value, key=lambda x: json.dumps(x, sort_keys=True))
    if op == "copy_filename_projection":
        if not isinstance(value, list):
            raise ValueError(f"{rule['rule_id']}: expected list")
        names = []
        for item in value:
            if isinstance(item, dict) and "rfilename" in item:
                names.append(item["rfilename"])
            elif isinstance(item, str):
                names.append(item)
        return True, sorted(names)
    raise ValueError(f"unsupported operation: {op}")


def build_exchange(native: dict[str, Any], native_ref: str, observed_at: str, kind: str = "model",
                   transport_profile: str = "InTr/SV-DN-1/v1") -> dict[str, Any]:
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    rules_hash = digest(mapping)
    semantic: dict[str, Any] = {}
    transformations = []
    lossy = []
    used_top = set()

    for rule in mapping["rules"]:
        present, value = project(rule, native)
        source = rule["source"][0]
        used_top.add(source.split(".")[0])
        tx = {
            "rule_id": rule["rule_id"],
            "source": rule["source"],
            "target": rule["target"],
            "operation": rule["operation"],
            "source_present": present,
            "lossless": bool(rule["lossless"]),
        }
        if present:
            set_path(semantic, rule["target"], value)
        transformations.append(tx)
        if present and not rule["lossless"]:
            lossy.append({
                "rule_id": rule["rule_id"],
                "target": rule["target"],
                "loss_note": rule.get("loss_note", "declared lossy transformation"),
                "native_preserved": True,
            })

    unmapped = {k: v for k, v in native.items() if k not in used_top}
    source_hash = digest(native)
    native_id = str(native.get("modelId") or native.get("id") or "")
    if not native_id:
        raise ValueError("native model identity is required")
    native_revision = native.get("sha")
    basis = {
        "source_system": "huggingface",
        "native_id": native_id,
        "native_revision": native_revision,
        "native_ref": native_ref,
        "observed_at": observed_at,
        "source_sha256": source_hash,
        "ruleset_hash": rules_hash,
    }
    exchange_id = digest(basis)
    tx_hash = digest({
        "exchange_id": exchange_id,
        "semantic": semantic,
        "transformations": transformations,
        "lossy_transformations": lossy,
        "source_sha256": source_hash,
    })
    return {
        "schema_version": "stegverse.sv-dn1.interlock-exchange/v1",
        "exchange_id": exchange_id,
        "source_system": "huggingface",
        "source_object": {
            "kind": kind,
            "native_id": native_id,
            "native_revision": native_revision,
            "native_ref": native_ref,
            "observed_at": observed_at,
        },
        "raw_evidence": {
            "source_sha256": source_hash,
            "preserved_native_fields": native,
            "unmapped_fields": unmapped,
        },
        "semantic_mapping": {
            "profile": "SV-DN-1-HF/v1",
            "ruleset_hash": rules_hash,
            "transformations": transformations,
            "lossy_transformations": lossy,
        },
        "semantic": semantic,
        "far_side_receipt": {
            "interlock_role": "SOURCE_SEMANTIC_ADAPTER",
            "transformation_hash": tx_hash,
            "authority_effect": "NONE",
        },
        "intr": {
            "transport_profile": transport_profile,
            "previous_receipt_hash": tx_hash,
            "authority_effect": "NONE",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--native-ref", required=True)
    ap.add_argument("--observed-at", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    native = json.loads(Path(args.input).read_text(encoding="utf-8"))
    exchange = build_exchange(native, args.native_ref, args.observed_at)
    Path(args.output).write_text(json.dumps(exchange, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": "HF_SIDE_INTERLOCK_PACKET_BUILT", "exchange_id": exchange["exchange_id"], "authority_effect": "NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
