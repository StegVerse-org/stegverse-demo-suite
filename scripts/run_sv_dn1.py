#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--native-ref", required=True)
    ap.add_argument("--observed-at", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    hf = load("sv_dn1_hf_interlock", "scripts/sv_dn1_hf_interlock.py")
    dest = load("sv_dn1_stegverse_interlock", "scripts/sv_dn1_stegverse_interlock.py")
    evaluator = load("sv_dn1_evaluator", "scripts/sv_dn1_evaluator.py")
    report = load("render_sv_dn1_report", "scripts/render_sv_dn1_report.py")
    dashboard = load("render_sv_dn1_dashboard", "scripts/render_sv_dn1_dashboard.py")
    pipeline_builder = load("build_sv_dn1_production_pipeline_observation", "scripts/build_sv_dn1_production_pipeline_observation.py")

    native = json.loads(Path(args.input).read_text(encoding="utf-8"))
    exchange = hf.build_exchange(native, args.native_ref, args.observed_at)
    admission = dest.bind_fixture_intake(exchange)
    if admission["state"] == "REJECTED":
        print(json.dumps(admission, sort_keys=True))
        return 2
    receipt = evaluator.evaluate(exchange, admission)
    pipeline = pipeline_builder.build(exchange, receipt)

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "exchange.json").write_text(json.dumps(exchange, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "admission.json").write_text(json.dumps(admission, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "result-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "production-pipeline-observation.json").write_text(json.dumps(pipeline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (out / "report.md").write_text(report.render(exchange, receipt, pipeline), encoding="utf-8")
    (out / "index.html").write_text(dashboard.render(exchange, receipt, 12, pipeline), encoding="utf-8")
    print(json.dumps({
        "state": "SV_DN1_FIXTURE_PIPELINE_COMPLETE",
        "exchange_id": exchange["exchange_id"],
        "receipt_id": receipt["receipt_id"],
        "sdk_binding": receipt["sdk_intake"]["binding_state"],
        "live_external_observation": False,
        "production_pipeline_publication_state": pipeline["publication_state"],
        "authority_effect": "NONE",
        "output_dir": str(out),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
