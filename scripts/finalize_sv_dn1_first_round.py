#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SDK_VALIDATE = load_module("sv_dn1_final_sdk_candidate_validate", "scripts/validate_sv_dn1_sdk_ingress_candidate.py")
SDK_BIND = load_module("sv_dn1_final_sdk_result_bind", "scripts/bind_sv_dn1_sdk_live_result.py")
EVAL = load_module("sv_dn1_final_evaluator", "scripts/sv_dn1_evaluator.py")
PIPE = load_module("sv_dn1_final_pipeline", "scripts/build_sv_dn1_production_pipeline_observation.py")
REPORT = load_module("sv_dn1_final_report", "scripts/render_sv_dn1_report.py")
DASH = load_module("sv_dn1_final_dashboard", "scripts/render_sv_dn1_dashboard.py")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path}: expected JSON object")
    return value


def validate_reconstruction(reconstruction: Mapping[str, Any], admission: Mapping[str, Any]) -> dict[str, Any]:
    rid = admission["sdk_intake"]["intake_receipt_id"]
    tx = admission["route"]["transaction_id"]
    require(reconstruction.get("manifest_receipt_id") == rid, "reconstruction manifest receipt mismatch")
    require(reconstruction.get("transaction_id") == tx, "reconstruction transaction mismatch")
    require(reconstruction.get("consequence_reexecuted") is False, "reconstruction reexecuted consequence")
    require(reconstruction.get("original_record_mutated") is False, "reconstruction mutated original record")
    require(
        reconstruction.get("operation_transition_custody_status") == "RECORDED",
        "reconstruction operation transitions are not in custody",
    )
    refs: list[str] = []
    op = reconstruction.get("operation_id")
    if isinstance(op, str) and op:
        refs.append(op)
    for key in ("operation_receipt_ids", "master_records_operation_receipts"):
        values = reconstruction.get(key)
        if isinstance(values, list):
            for value in values:
                if isinstance(value, str) and value:
                    refs.append(value)
                elif isinstance(value, Mapping):
                    for candidate in ("event_receipt_id", "receipt_id"):
                        ref = value.get(candidate)
                        if isinstance(ref, str) and ref:
                            refs.append(ref)
                            break
    refs.extend([rid, tx])
    return {
        "state": "PASS",
        "manifest_receipt_id": rid,
        "transaction_id": tx,
        "operation_transition_custody_status": "RECORDED",
        "consequence_reexecuted": False,
        "original_record_mutated": False,
        "evidence_refs": list(dict.fromkeys(refs)),
    }


def validate_replay(replay: Mapping[str, Any] | None, admission: Mapping[str, Any]) -> dict[str, Any] | None:
    if replay is None:
        return None
    rid = admission["sdk_intake"]["intake_receipt_id"]
    require(replay.get("manifest_receipt_id") == rid, "replay manifest receipt mismatch")
    require(replay.get("deterministic_disposition_match") is True, "replay disposition mismatch")
    if "candidate_identity_match" in replay:
        require(replay.get("candidate_identity_match") is True, "replay candidate identity mismatch")
    require(replay.get("consequence_reexecuted") is False, "replay reexecuted consequence")
    require(replay.get("original_record_mutated") is False, "replay mutated original record")
    require(replay.get("operation_transition_custody_status") == "RECORDED", "replay operation not in custody")
    return dict(replay)


def base_lane_evidence(
    capture: Mapping[str, Any],
    exchange: Mapping[str, Any],
    intr: Mapping[str, Any],
    admission: Mapping[str, Any],
    sdk_result: Mapping[str, Any],
    result_receipt: Mapping[str, Any],
    reconstruction: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    none = []
    return {
        "external_source_capture": {
            "state": "PASS",
            "evidence_refs": [capture["capture_id"], capture["raw_sha256"]],
            "known_errors": none,
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "hf_facing_interlock": {
            "state": "PASS",
            "evidence_refs": [exchange["exchange_id"], exchange["far_side_receipt"]["transformation_hash"]],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "intr": {
            "state": "PASS",
            "evidence_refs": [intr["receipt_hash"]],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "stegverse_interlock": {
            "state": "PASS",
            "evidence_refs": [exchange["exchange_id"], intr["receipt_hash"]],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "sdk_ingress": {
            "state": "PASS",
            "evidence_refs": [
                admission["sdk_intake"]["manifest_hash"],
                admission["sdk_intake"]["intake_receipt_id"],
                admission["sdk_result_binding_hash"],
            ],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "stegcore_steggate": {
            "state": "PASS",
            "evidence_refs": [
                sdk_result["result_binding_hash"],
                f"governance:{admission['governance_state']}",
            ],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "master_records_custody": {
            "state": "PASS",
            "evidence_refs": [admission["sdk_intake"]["intake_receipt_id"]],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "reconstruction": {
            "state": "PASS",
            "evidence_refs": list(reconstruction["evidence_refs"]),
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
        "public_projection": {
            "state": "PASS",
            "evidence_refs": [result_receipt["receipt_id"]],
            "known_errors": [],
            "unknowns": [],
            "authority_effect": "NONE",
        },
    }


def apply_lane_findings(
    lanes: dict[str, dict[str, Any]],
    findings: Mapping[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if findings is None:
        return lanes
    allowed = {"FAIL", "DEGRADED", "UNKNOWN"}
    for name, raw in findings.items():
        require(name in lanes, f"unknown production lane finding: {name}")
        require(isinstance(raw, Mapping), f"{name}: finding must be object")
        state = raw.get("state")
        require(state in allowed, f"{name}: findings may only downgrade to FAIL/DEGRADED/UNKNOWN")
        errors = raw.get("known_errors") or []
        unknowns = raw.get("unknowns") or []
        refs = raw.get("evidence_refs") or []
        require(isinstance(errors, list) and all(isinstance(x, str) for x in errors), f"{name}: invalid known_errors")
        require(isinstance(unknowns, list) and all(isinstance(x, str) for x in unknowns), f"{name}: invalid unknowns")
        require(isinstance(refs, list) and all(isinstance(x, str) for x in refs), f"{name}: invalid evidence_refs")
        if state in {"FAIL", "DEGRADED"}:
            require(bool(errors), f"{name}: {state} requires explicit known_errors")
        if state == "UNKNOWN":
            require(bool(unknowns), f"{name}: UNKNOWN requires explicit unknowns")
        lanes[name] = {
            "state": state,
            "evidence_refs": list(dict.fromkeys(lanes[name]["evidence_refs"] + refs)),
            "known_errors": errors,
            "unknowns": unknowns,
            "authority_effect": "NONE",
        }
    return lanes


def finalize(
    *,
    capture: dict[str, Any],
    exchange: dict[str, Any],
    intr: dict[str, Any],
    candidate: dict[str, Any],
    sdk_result: dict[str, Any],
    admission: dict[str, Any],
    result_receipt: dict[str, Any],
    reconstruction: dict[str, Any],
    replay: dict[str, Any] | None = None,
    lane_findings: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    require(capture.get("schema_version") == "stegverse.sv-dn1.source-capture/v1", "wrong source capture schema")
    require(capture.get("source_system") == "huggingface", "wrong source system")
    require(capture.get("claims", {}).get("credential_used") is False, "credentialed capture not admitted")
    require(capture.get("claims", {}).get("hugging_face_endorsement_claimed") is False, "external endorsement claim forbidden")
    require(exchange.get("exchange_id") == candidate.get("exchange", {}).get("exchange_id"), "candidate/exchange mismatch")
    require(intr.get("receipt_hash") == candidate.get("intr_runtime_receipt", {}).get("receipt_hash"), "candidate/InTr mismatch")

    blockers = SDK_VALIDATE.validate(candidate)
    require(not blockers, "candidate validation failed: " + ",".join(blockers))
    expected_admission = SDK_BIND.bind(candidate, sdk_result)
    require(admission == expected_admission, "SDK admission object does not match canonical result binding")

    expected_receipt = EVAL.evaluate(exchange, admission)
    require(result_receipt == expected_receipt, "SV-DN-1 result receipt does not match deterministic evaluation")

    reconstructed = validate_reconstruction(reconstruction, admission)
    replayed = validate_replay(replay, admission)

    lanes = base_lane_evidence(capture, exchange, intr, admission, sdk_result, result_receipt, reconstructed)
    lanes = apply_lane_findings(lanes, lane_findings)
    pipeline = PIPE.build(exchange, result_receipt, lanes)
    require(pipeline["observation_class"] == "LIVE", "first-round analysis requires LIVE observation class")
    require(pipeline["publication_state"] != "WITHHELD", "first-round production pipeline remains WITHHELD")

    external_unknowns = sorted(
        name for name, value in result_receipt["dimensions"].items() if value["state"] == "UNKNOWN"
    )
    external_failures = sorted(
        name for name, value in result_receipt["dimensions"].items() if value["state"] == "FAIL"
    )
    analysis = {
        "schema_version": "stegverse.sv-dn1.first-round-analysis/v1",
        "state": "ANALYZED",
        "profile_id": "SV-DN-1",
        "exchange_id": exchange["exchange_id"],
        "manifest_receipt_id": admission["sdk_intake"]["intake_receipt_id"],
        "governance_state": admission["governance_state"],
        "external_evaluation": {
            "result_receipt_id": result_receipt["receipt_id"],
            "summary": result_receipt["summary"],
            "dimension_states": {k: v["state"] for k, v in result_receipt["dimensions"].items()},
            "failures": external_failures,
            "unknowns": external_unknowns,
        },
        "production_pipeline": pipeline,
        "reconstruction": reconstructed,
        "replay": replayed,
        "artifacts": {
            "result_receipt": "result-receipt.json",
            "production_pipeline_observation": "production-pipeline-observation.json",
            "report": "report.md",
            "dashboard": "index.html",
        },
        "claims": {
            "first_round_analyzed": True,
            "dashboard_generated": True,
            "dashboard_publicly_hosted": False,
            "certification_claimed": False,
            "production_perfection_claimed": False,
        },
        "authority_effect": "NONE",
    }
    return analysis, pipeline


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--intr-receipt", required=True)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--sdk-result", required=True)
    ap.add_argument("--admission", required=True)
    ap.add_argument("--result-receipt", required=True)
    ap.add_argument("--reconstruction", required=True)
    ap.add_argument("--replay")
    ap.add_argument("--lane-findings")
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    replay = load_object(Path(args.replay)) if args.replay else None
    findings = load_object(Path(args.lane_findings)) if args.lane_findings else None
    capture = load_object(Path(args.capture))
    exchange = load_object(Path(args.exchange))
    result_receipt = load_object(Path(args.result_receipt))
    analysis, pipeline = finalize(
        capture=capture,
        exchange=exchange,
        intr=load_object(Path(args.intr_receipt)),
        candidate=load_object(Path(args.candidate)),
        sdk_result=load_object(Path(args.sdk_result)),
        admission=load_object(Path(args.admission)),
        result_receipt=result_receipt,
        reconstruction=load_object(Path(args.reconstruction)),
        replay=replay,
        lane_findings=findings,
    )

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "first-round-analysis.json").write_text(json.dumps(analysis, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "production-pipeline-observation.json").write_text(json.dumps(pipeline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "result-receipt.json").write_text(json.dumps(result_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "report.md").write_text(REPORT.render(exchange, result_receipt, pipeline), encoding="utf-8")
    (out / "index.html").write_text(DASH.render(exchange, result_receipt, 12, pipeline), encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_FIRST_ROUND_ANALYZED",
        "exchange_id": analysis["exchange_id"],
        "manifest_receipt_id": analysis["manifest_receipt_id"],
        "publication_state": pipeline["publication_state"],
        "external_summary": analysis["external_evaluation"]["summary"],
        "external_unknowns": analysis["external_evaluation"]["unknowns"],
        "external_failures": analysis["external_evaluation"]["failures"],
        "dashboard_generated": True,
        "dashboard_publicly_hosted": False,
        "authority_effect": "NONE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
