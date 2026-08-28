#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(exchange: dict, receipt: dict, pipeline: dict | None = None) -> str:
    src = exchange["source_object"]
    lines = [
        "# SV-DN-1 Evaluation Report",
        "",
        f"- Profile: {receipt['profile_id']}",
        f"- Receipt: {receipt['receipt_id']}",
        f"- Exchange: {receipt['exchange_id']}",
        f"- Source: huggingface / {src['native_id']}",
        f"- Revision: {src['native_revision']}",
        f"- Observed at: {src['observed_at']}",
        f"- SDK binding: {receipt['sdk_intake']['binding_state']}",
        "- Authority effect: NONE",
        "- External endorsement claimed: false",
        "",
        "## Dimension results",
        "",
        "| Dimension | State | Evidence basis |",
        "|---|---|---|",
    ]
    for name, result in sorted(receipt["dimensions"].items()):
        basis = "<br>".join(str(x) for x in result["basis"])
        lines.append(f"| {name} | **{result['state']}** | {basis} |")
    lines += [
        "",
        "## Summary",
        "",
        f"- PASS: {receipt['summary']['pass']}",
        f"- FAIL: {receipt['summary']['fail']}",
        f"- UNKNOWN: {receipt['summary']['unknown']}",
        f"- NOT_APPLICABLE: {receipt['summary']['not_applicable']}",
    ]
    if pipeline is not None:
        lines += [
            "",
            "## StegVerse production pipeline under observation",
            "",
            f"- Observation class: {pipeline['observation_class']}",
            f"- Publication state: {pipeline['publication_state']}",
            f"- First unresolved pipeline boundary: {pipeline.get('first_unresolved_pipeline_boundary')}",
            "- Production perfection claimed: false",
            "",
            "| Production lane | State | Known errors | Unknowns | Evidence refs |",
            "|---|---|---|---|---|",
        ]
        for name, lane in pipeline["lanes"].items():
            errors = "<br>".join(lane.get("known_errors", [])) or "—"
            unknowns = "<br>".join(lane.get("unknowns", [])) or "—"
            refs = "<br>".join(lane.get("evidence_refs", [])) or "—"
            lines.append(f"| {name} | **{lane['state']}** | {errors} | {unknowns} | {refs} |")
        lines += [
            "",
            "Public readiness is bounded confidence, not perfection. Known failures and unknowns are part of the published evidence when they are explicit, bounded, and reconstructable.",
        ]
    lines += [
        "",
        "## Interpretation boundary",
        "",
        "This report records a bounded SV-DN-1 evaluation. It is not a claim that Hugging Face",
        "operates or endorses the reference Interlock, is not certification, and is not enforcement.",
        "UNKNOWN is preserved when the admitted evidence does not support a stronger conclusion.",
        "",
        "## Evidence chain",
        "",
    ]
    lines += [f"- {x}" for x in receipt["evidence_chain"]]
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--pipeline-observation")
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    pipeline = json.loads(Path(args.pipeline_observation).read_text(encoding="utf-8")) if args.pipeline_observation else None
    Path(args.output).write_text(render(exchange, receipt, pipeline), encoding="utf-8")
    print(json.dumps({"state":"SV_DN1_REPORT_RENDERED","output":args.output,"receipt_id":receipt["receipt_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
