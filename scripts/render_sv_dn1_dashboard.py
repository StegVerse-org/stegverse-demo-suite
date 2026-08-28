#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def render(exchange: dict, receipt: dict, target_refresh_hours: int = 12, pipeline: dict | None = None) -> str:
    src = exchange["source_object"]
    summary = receipt["summary"]
    cards = "".join(
        f'<div class="metric"><div class="n">{summary[k]}</div><div class="k">{esc(k.upper())}</div></div>'
        for k in ("pass","fail","unknown","not_applicable")
    )
    rows = "".join(
        "<tr>"
        f"<td>{esc(name)}</td>"
        f"<td><span class=\"state {esc(result['state'].lower())}\">{esc(result['state'])}</span></td>"
        f"<td>{'<br>'.join(esc(x) for x in result['basis'])}</td>"
        "</tr>"
        for name, result in sorted(receipt["dimensions"].items())
    )
    chain = "".join(f"<li><code>{esc(x)}</code></li>" for x in receipt["evidence_chain"])
    live = receipt["sdk_intake"]["binding_state"] == "SDK_ADMITTED"
    live_label = "SDK_ADMITTED" if live else "FIXTURE / NOT LIVE-ADMITTED"
    pipeline_section = ""
    if pipeline is not None:
        lane_rows = "".join(
            "<tr>"
            f"<td>{esc(name)}</td>"
            f"<td><span class=\\\"state {esc(lane['state'].lower())}\\\">{esc(lane['state'])}</span></td>"
            f"<td>{'<br>'.join(esc(x) for x in lane.get('known_errors', [])) or '—'}</td>"
            f"<td>{'<br>'.join(esc(x) for x in lane.get('unknowns', [])) or '—'}</td>"
            f"<td>{'<br>'.join(f'<code>{esc(x)}</code>' for x in lane.get('evidence_refs', [])) or '—'}</td>"
            "</tr>"
            for name, lane in pipeline["lanes"].items()
        )
        first_unresolved = pipeline.get("first_unresolved_pipeline_boundary") or "none"
        pipeline_section = f"""
<section>
<h2>StegVerse production pipeline under observation</h2>
<div class="banner"><strong>Public-readiness principle:</strong> This is the production side being evaluated as it operates. Public readiness does not require perfection; it requires errors and unknowns to be bounded, visible, evidence-backed, and reconstructable.</div>
<p><strong>Observation class:</strong> {esc(pipeline["observation_class"])}<br>
<strong>Publication state:</strong> {esc(pipeline["publication_state"])}<br>
<strong>First unresolved pipeline boundary:</strong> {esc(first_unresolved)}<br>
<strong>Production perfection claimed:</strong> false</p>
<table>
<thead><tr><th>Production lane</th><th>Observed state</th><th>Known errors</th><th>Unknowns</th><th>Evidence</th></tr></thead>
<tbody>{lane_rows}</tbody>
</table>
</section>
"""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>StegVerse SV-DN-1 Evaluation</title>
<style>
:root {{ font-family: system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; color-scheme: light dark; }}
body {{ max-width: 1180px; margin: 0 auto; padding: 24px; line-height: 1.45; }}
header {{ border-bottom: 1px solid #8886; padding-bottom: 18px; margin-bottom: 20px; }}
.banner {{ padding: 12px 14px; border: 1px solid #8888; border-radius: 10px; margin: 12px 0; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit,minmax(150px,1fr)); gap: 12px; margin: 18px 0; }}
.metric {{ border: 1px solid #8886; border-radius: 12px; padding: 16px; }}
.metric .n {{ font-size: 2rem; font-weight: 700; }}
.metric .k {{ opacity: .7; font-size: .8rem; }}
table {{ width:100%; border-collapse: collapse; margin: 18px 0; }}
th,td {{ text-align:left; border-bottom:1px solid #8885; padding:10px 8px; vertical-align:top; }}
.state {{ font-weight:700; }}
.pass {{ color: #16803a; }} .fail {{ color:#b42318; }} .unknown,.degraded {{ color:#9a6700; }} .not_observed,.not_reached,.not_applicable {{ opacity:.7; }}
code {{ overflow-wrap:anywhere; }}
.small {{ opacity:.72; font-size:.9rem; }}
</style>
</head>
<body>
<header>
<h1>StegVerse SV-DN-1</h1>
<p>Public model-distribution neutrality &amp; portability evaluation</p>
<div class="banner"><strong>Transparency boundary:</strong> This page is generated from the exact result receipt below. It does not claim Hugging Face endorsement, Hugging Face operation of the reference Interlock, certification, or enforcement authority.</div>
</header>

<section>
<h2>Current observation</h2>
<p><strong>Source:</strong> Hugging Face-facing public surface<br>
<strong>Artifact:</strong> {esc(src["native_id"])}<br>
<strong>Revision:</strong> {esc(src["native_revision"])}<br>
<strong>Observed:</strong> {esc(src["observed_at"])}<br>
<strong>Admission state:</strong> {esc(live_label)}<br>
<strong>Target refresh:</strong> up to every {target_refresh_hours} hours when an admitted resident observer is available, plus material-delta updates.</p>
</section>

<section class="grid">{cards}</section>\n\n{pipeline_section}

<section>
<h2>Evaluation dimensions</h2>
<table>
<thead><tr><th>Dimension</th><th>State</th><th>Evidence basis</th></tr></thead>
<tbody>{rows}</tbody>
</table>
</section>

<section>
<h2>Semantic transformation</h2>
<p>The Hugging Face-facing Interlock normalized this observation using <code>{esc(exchange["semantic_mapping"]["profile"])}</code>.
The mapping ruleset hash is <code>{esc(exchange["semantic_mapping"]["ruleset_hash"])}</code>.</p>
<p>Declared lossy transformations: <strong>{len(exchange["semantic_mapping"]["lossy_transformations"])}</strong>.
Unmapped top-level fields preserved: <strong>{len(exchange["raw_evidence"]["unmapped_fields"])}</strong>.</p>
</section>

<section>
<h2>Receipt chain</h2>
<p><strong>Result receipt:</strong> <code>{esc(receipt["receipt_id"])}</code><br>
<strong>Exchange:</strong> <code>{esc(receipt["exchange_id"])}</code><br>
<strong>SDK binding:</strong> <code>{esc(receipt["sdk_intake"]["binding_state"])}</code></p>
<ol>{chain}</ol>
</section>

<footer class="small">
<p>Evaluation identifies what admitted evidence supports. Governance and downstream enforcement are separate authorities. UNKNOWN is not silently promoted to PASS or FAIL.</p>
</footer>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--pipeline-observation")
    ap.add_argument("--target-refresh-hours", type=int, default=12)
    args = ap.parse_args()
    exchange = json.loads(Path(args.exchange).read_text(encoding="utf-8"))
    receipt = json.loads(Path(args.receipt).read_text(encoding="utf-8"))
    pipeline = json.loads(Path(args.pipeline_observation).read_text(encoding="utf-8")) if args.pipeline_observation else None
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(exchange, receipt, args.target_refresh_hours, pipeline), encoding="utf-8")
    print(json.dumps({"state":"SV_DN1_DASHBOARD_RENDERED","output":str(out),"receipt_id":receipt["receipt_id"],"static":True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
