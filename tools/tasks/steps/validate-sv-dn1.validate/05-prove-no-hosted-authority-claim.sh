python - <<'PY'
from pathlib import Path
forbidden = ("GITHUB_TOKEN", "github.token", "secrets.", "contents: write", "actions: write")
paths = [
    Path("scripts/sv_dn1_hf_interlock.py"),
    Path("scripts/sv_dn1_stegverse_interlock.py"),
    Path("scripts/sv_dn1_evaluator.py"),
    Path("scripts/run_sv_dn1.py"),
    Path("scripts/render_sv_dn1_dashboard.py"),
    Path("scripts/build_sv_dn1_sdk_ingress_manifest.py"),
    Path("scripts/validate_sv_dn1_sdk_ingress_candidate.py"),
    Path("scripts/build_sv_dn1_production_pipeline_observation.py"),
    Path("scripts/bind_sv_dn1_sdk_live_result.py"),
    Path("scripts/finalize_sv_dn1_first_round.py"),
    Path("scripts/verify_sv_dn1_public_publication.py"),
]
for path in paths:
    text = path.read_text()
    for token in forbidden:
        assert token not in text, (path, token)
print("SV_DN1_NO_HOSTED_AUTHORITY_PASS")
PY
