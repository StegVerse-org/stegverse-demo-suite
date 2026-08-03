from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import validate_demo  # noqa: E402


class GovernedDigitalRightsDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.case = json.loads((HERE / "demo_case.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((ROOT / "schemas" / "governed_digital_rights_demo.schema.json").read_text(encoding="utf-8"))
        cls.task_state = json.loads((HERE / "task_state.json").read_text(encoding="utf-8"))

    def test_schema_contract_is_bound(self) -> None:
        validate_demo.validate_schema_document(self.schema)

    def test_canonical_case_completes_with_deterministic_receipt(self) -> None:
        first = validate_demo.evaluate_case(copy.deepcopy(self.case), copy.deepcopy(self.task_state))
        second = validate_demo.evaluate_case(copy.deepcopy(self.case), copy.deepcopy(self.task_state))
        self.assertEqual(first["status"], "COMPLETE")
        self.assertEqual(first["receipt_sha256"], second["receipt_sha256"])
        self.assertTrue(first["checks"]["unauthorized_transition_denied"])
        self.assertTrue(first["checks"]["authorized_future_amendment_applied"])
        self.assertTrue(first["checks"]["historical_period_preserved"])

    def test_unauthorized_change_is_denied_and_does_not_change_period_one(self) -> None:
        receipt = validate_demo.evaluate_case(copy.deepcopy(self.case))
        denied = receipt["transition_decisions"][0]
        period_one = receipt["usage_allocations"][0]
        self.assertEqual(denied["decision"], "DENY")
        self.assertEqual(denied["reason"], "MISSING_REQUIRED_SIGNATURES")
        self.assertEqual(period_one["active_shares_basis_points"], {"artist": 5000, "producer": 2500, "label": 2500})
        self.assertEqual(period_one["allocation_cents"], {"artist": 5000, "producer": 2500, "label": 2500})

    def test_authorized_amendment_applies_only_after_effective_time(self) -> None:
        receipt = validate_demo.evaluate_case(copy.deepcopy(self.case))
        period_one, period_two = receipt["usage_allocations"]
        self.assertEqual(period_one["rights_source"], "initial_rights")
        self.assertEqual(period_two["rights_source"], "transition-authorized-artist-to-producer")
        self.assertEqual(period_two["allocation_cents"], {"artist": 4000, "producer": 3500, "label": 2500})

    def test_invalid_share_total_fails_closed(self) -> None:
        changed = copy.deepcopy(self.case)
        changed["initial_rights"]["shares_basis_points"]["artist"] = 4999
        with self.assertRaises(validate_demo.ValidationError):
            validate_demo.evaluate_case(changed)

    def test_missing_required_signature_cannot_be_relabelled_allow(self) -> None:
        changed = copy.deepcopy(self.case)
        changed["transitions"][1]["signatures"] = ["artist", "producer"]
        with self.assertRaises(validate_demo.ValidationError):
            validate_demo.evaluate_case(changed)

    def test_retroactive_amendment_fails_expected_allow_assertion(self) -> None:
        changed = copy.deepcopy(self.case)
        changed["transitions"][1]["effective_at"] = "2026-07-01T00:00:00Z"
        with self.assertRaises(validate_demo.ValidationError):
            validate_demo.evaluate_case(changed)

    def test_stale_claim_is_machine_observable(self) -> None:
        observed = validate_demo.validate_claim_state(
            copy.deepcopy(self.task_state),
            now=datetime(2026, 8, 5, tzinfo=timezone.utc),
        )
        self.assertTrue(observed["stale"])

    def test_cli_writes_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "receipt.json"
            exit_code = validate_demo.main(
                [
                    "--input",
                    str(HERE / "demo_case.json"),
                    "--schema",
                    str(ROOT / "schemas" / "governed_digital_rights_demo.schema.json"),
                    "--task-state",
                    str(HERE / "task_state.json"),
                    "--output",
                    str(output),
                ]
            )
            self.assertEqual(exit_code, 0)
            saved = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "COMPLETE")
            self.assertIn("receipt_sha256", saved)


if __name__ == "__main__":
    unittest.main()
