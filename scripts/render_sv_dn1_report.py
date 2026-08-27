#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def render(exchange: dict, receipt: dict) -> str:
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
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    Path(args.output).write_text(render(exchange, receipt), encoding="utf-8")
    print(json.dumps({"state":"SV_DN1_REPORT_RENDERED","output":args.output,"receipt_id":receipt["receipt_id"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
