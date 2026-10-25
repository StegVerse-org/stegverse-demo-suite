python - <<'PY'
import json
from pathlib import Path
p = Path("/tmp/sv-dn1-proof")
receipt = json.loads((p / "result-receipt.json").read_text())
pipeline = json.loads((p / "production-pipeline-observation.json").read_text())
html = (p / "index.html").read_text()
assert receipt["sdk_intake"]["binding_state"] == "FIXTURE_BOUND"
assert receipt["claims"]["live_double_interlock_traversal_claimed"] is False
assert receipt["claims"]["certification_claimed"] is False
assert pipeline["observation_class"] == "FIXTURE"
assert pipeline["publication_state"] == "WITHHELD"
assert pipeline["claims"]["production_perfection_claimed"] is False
assert all(x["state"] in ("NOT_OBSERVED", "NOT_APPLICABLE") for x in pipeline["lanes"].values())
assert "StegVerse production pipeline under observation" in html
assert "FIXTURE / NOT LIVE-ADMITTED" in html
assert "<script" not in html.lower()
print("SV_DN1_VALIDATION_PASS")
PY
