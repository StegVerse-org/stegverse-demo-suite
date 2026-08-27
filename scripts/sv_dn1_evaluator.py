#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE = json.loads((ROOT / "config" / "sv_dn1_profile.json").read_text(encoding="utf-8"))


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical(value)).hexdigest()


def result(state: str, *basis: str) -> dict[str, Any]:
    return {"state": state, "basis": list(basis)}


def evaluate(exchange: dict[str, Any], admission: dict[str, Any]) -> dict[str, Any]:
    if admission.get("state") not in ("ADMITTED_FOR_FIXTURE_EVALUATION", "SDK_ADMITTED"):
        raise ValueError("exchange is not admitted")
    semantic = exchange.get("semantic", {}).get("artifact", {})
    native = exchange.get("raw_evidence", {}).get("preserved_native_fields", {})
    tags = {str(x).lower() for x in semantic.get("tags", []) if isinstance(x, (str, int, float))}
    files = {str(x).lower() for x in semantic.get("files", [])}
    dimensions: dict[str, dict[str, Any]] = {}

    dimensions["artifact_identity"] = result(
        "PASS" if semantic.get("identity") and semantic.get("revision") else "UNKNOWN",
        "HF-ID-001", "HF-REV-001",
    )
    dimensions["license_and_gating"] = result(
        "PASS" if semantic.get("license") else "UNKNOWN",
        "HF-LICENSE-001" if semantic.get("license") else "license_not_observed",
    )
    export_signal = bool(files) and any(name.endswith((".safetensors", ".bin", ".gguf", ".onnx")) for name in files)
    dimensions["exportability"] = result("PASS" if export_signal else "UNKNOWN", "artifact_files" if export_signal else "no_export_artifact_signal")
    local_signal = any("gguf" in name or "onnx" in name for name in files) or "transformers" in tags
    dimensions["local_offline_execution"] = result("PASS" if local_signal else "UNKNOWN", "artifact_files/tags" if local_signal else "no_local_execution_signal")

    dimensions["cpu_portability"] = result("PASS" if ("cpu" in tags or any("gguf" in n for n in files)) else "UNKNOWN", "tags/files")
    dimensions["amd_rocm_portability"] = result("PASS" if any("rocm" in t or "amd" in t for t in tags) else "UNKNOWN", "tags")
    dimensions["nvidia_cuda_portability"] = result("PASS" if any("cuda" in t or "nvidia" in t for t in tags) else "UNKNOWN", "tags")
    dimensions["other_accelerator_portability"] = result("PASS" if any(t in tags for t in ("tpu","mps","openvino","directml")) else "UNKNOWN", "tags")

    vendor_specific = any("cuda" in t or "nvidia" in t for t in tags)
    if vendor_specific:
        dimensions["vendor_specific_dependency"] = result("FAIL", "vendor_specific_tag_observed")
    else:
        dimensions["vendor_specific_dependency"] = result("UNKNOWN", "absence_of_tag_is_not_proof_of_absence")

    dimensions["observable_default_or_recommendation_bias"] = result("UNKNOWN", "requires_distribution_surface_observation")
    dimensions["benchmark_method_consistency"] = result("UNKNOWN", "requires_comparable_benchmark_evidence")
    dimensions["migration_exit_path"] = result("PASS" if export_signal else "UNKNOWN", "exportable_artifact_signal" if export_signal else "no_exit_path_signal")
    dimensions["deterministic_reconstruction"] = result("PASS", exchange["raw_evidence"]["source_sha256"], exchange["semantic_mapping"]["ruleset_hash"])

    counts = {"pass": 0, "fail": 0, "unknown": 0, "not_applicable": 0}
    for d in dimensions.values():
        counts[d["state"].lower()] += 1

    claims = {
        "external_endorsement_claimed": False,
        "hugging_face_operated_interlock_claimed": False,
        "live_double_interlock_traversal_claimed": admission["sdk_intake"]["binding_state"] == "SDK_ADMITTED",
        "certification_claimed": False,
        "evaluation_is_enforcement": False,
    }
    body = {
        "schema_version": "stegverse.sv-dn1.result-receipt/v1",
        "profile_id": "SV-DN-1",
        "exchange_id": exchange["exchange_id"],
        "sdk_intake": admission["sdk_intake"],
        "dimensions": dimensions,
        "summary": counts,
        "evidence_chain": [
            exchange["raw_evidence"]["source_sha256"],
            exchange["semantic_mapping"]["ruleset_hash"],
            exchange["far_side_receipt"]["transformation_hash"],
            exchange["intr"]["previous_receipt_hash"],
            admission["sdk_intake"]["manifest_hash"],
            admission["sdk_intake"]["intake_receipt_id"],
        ],
        "claims": claims,
        "authority_effect": "NONE",
    }
    body["receipt_id"] = digest(body)
    return body


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--admission", required=True)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    admission = json.loads(Path(args.admission).read_text(encoding="utf-8"))
    receipt = evaluate(exchange, admission)
    Path(args.output).write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"state": "SV_DN1_EVALUATED", "receipt_id": receipt["receipt_id"], "summary": receipt["summary"], "authority_effect": "NONE"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
