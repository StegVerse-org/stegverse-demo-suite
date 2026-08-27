from __future__ import annotations

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name: str, rel: str):
    path = ROOT / rel
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


OBS = load("sv_dn1_observer_test", "scripts/observe_sv_dn1_hf_public.py")
HIST = load("sv_dn1_history_test", "scripts/build_sv_dn1_dashboard_history.py")
HF = load("sv_dn1_hf_for_observer_test", "scripts/sv_dn1_hf_interlock.py")
DEST = load("sv_dn1_dest_for_observer_test", "scripts/sv_dn1_stegverse_interlock.py")
EVAL = load("sv_dn1_eval_for_observer_test", "scripts/sv_dn1_evaluator.py")


class FakeResponse:
    def __init__(self, raw: bytes, url: str, content_type: str = "application/json", status: int = 200):
        self._raw = io.BytesIO(raw)
        self._url = url
        self.status = status
        self.headers = {"Content-Type": content_type}

    def read(self, size: int = -1):
        return self._raw.read(size)

    def geturl(self):
        return self._url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class SvDn1PublicObserverTests(unittest.TestCase):
    def test_url_boundary_rejects_non_huggingface(self) -> None:
        self.assertTrue(OBS.allowed_hf_url("https://huggingface.co/api/models/example"))
        self.assertTrue(OBS.allowed_hf_url("https://cdn-lfs.huggingface.co/path"))
        self.assertFalse(OBS.allowed_hf_url("http://huggingface.co/api/models/example"))
        self.assertFalse(OBS.allowed_hf_url("https://example.com/api/models/example"))

    def test_capture_is_public_non_authorizing_and_raw_hash_bound(self) -> None:
        raw = b'{"modelId":"fixture/model","sha":"abc"}'
        def opener(request, timeout=20.0):
            return FakeResponse(raw, "https://huggingface.co/api/models/fixture/model")
        capture = OBS.capture_public_json(
            "https://huggingface.co/api/models/fixture/model",
            "2026-08-27T18:00:00Z",
            opener=opener,
        )
        self.assertEqual(capture["parsed_json"]["modelId"], "fixture/model")
        self.assertTrue(capture["claims"]["public_source_only"])
        self.assertFalse(capture["claims"]["credential_used"])
        self.assertFalse(capture["claims"]["hugging_face_endorsement_claimed"])
        self.assertFalse(capture["claims"]["live_interlock_traversal_claimed"])
        self.assertEqual(capture["authority_effect"], "NONE")
        self.assertEqual(capture["raw_sha256"], OBS.raw_digest(raw))

    def test_capture_rejects_redirect_outside_hf_boundary(self) -> None:
        raw = b'{"ok":true}'
        def opener(request, timeout=20.0):
            return FakeResponse(raw, "https://example.com/redirected")
        with self.assertRaises(ValueError):
            OBS.capture_public_json(
                "https://huggingface.co/api/models/fixture/model",
                "2026-08-27T18:00:00Z",
                opener=opener,
            )

    def test_capture_rejects_non_json(self) -> None:
        raw = b"<html>not json</html>"
        def opener(request, timeout=20.0):
            return FakeResponse(raw, "https://huggingface.co/api/models/fixture/model", "text/html")
        with self.assertRaises(ValueError):
            OBS.capture_public_json(
                "https://huggingface.co/api/models/fixture/model",
                "2026-08-27T18:00:00Z",
                opener=opener,
            )

    def test_history_records_revision_and_dimension_deltas(self) -> None:
        native = json.loads((ROOT / "fixtures/sv_dn1/hf_model_baseline.json").read_text(encoding="utf-8"))
        e1 = HF.build_exchange(native, "https://huggingface.co/fixture", "2026-08-27T12:00:00Z")
        a1 = DEST.bind_fixture_intake(e1)
        r1 = EVAL.evaluate(e1, a1)

        native2 = dict(native)
        native2["sha"] = "fedcba9876543210fedcba9876543210fedcba98"
        native2["tags"] = list(native["tags"]) + ["cuda"]
        e2 = HF.build_exchange(native2, "https://huggingface.co/fixture", "2026-08-28T00:00:00Z")
        a2 = DEST.bind_fixture_intake(e2)
        r2 = EVAL.evaluate(e2, a2)

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for idx, (e, r) in enumerate(((e1, r1), (e2, r2)), start=1):
                d = root / str(idx)
                d.mkdir()
                (d / "exchange.json").write_text(json.dumps(e), encoding="utf-8")
                (d / "result-receipt.json").write_text(json.dumps(r), encoding="utf-8")
            history = HIST.build_history([root / "1", root / "2"])

        self.assertEqual(history["observation_count"], 2)
        delta = history["entries"][1]["delta_from_previous"]
        self.assertTrue(delta["revision_changed"])
        self.assertIn("nvidia_cuda_portability", delta["dimension_changes"])
        self.assertIn("vendor_specific_dependency", delta["dimension_changes"])
        self.assertEqual(history["authority_effect"], "NONE")

    def test_schedule_is_twice_daily_target_not_github_runtime_authority(self) -> None:
        schedule = json.loads((ROOT / "config/sv_dn1_observation_schedule.json").read_text(encoding="utf-8"))
        self.assertEqual(schedule["target_refresh_hours"], 12)
        self.assertFalse(schedule["github_actions_production_observer"])
        self.assertFalse(schedule["github_actions_control_plane"])
        self.assertEqual(schedule["credential_authority"], "TV/TVC")
        self.assertEqual(schedule["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
