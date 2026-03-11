from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Dict, List


@dataclass
class ActionReceipt:
    receipt_id: str
    action_name: str
    decision: str
    reason: str
    current_state: str
    required_state: str
    previous_receipt_id: str
    timestamp_utc: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "action_name": self.action_name,
            "decision": self.decision,
            "reason": self.reason,
            "current_state": self.current_state,
            "required_state": self.required_state,
            "previous_receipt_id": self.previous_receipt_id,
            "timestamp_utc": self.timestamp_utc,
            "receipt_hash": self.receipt_hash,
        }


class ActionGate:
    """
    Receipt-governed action execution boundary for the StegVerse demo suite.

    This module does not execute real infrastructure mutations.
    It simulates action approval / denial and records action receipts.
    """

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.policy_path = self.repo_root / "engine" / "actions" / "actions.json"
        self.runtime_dir = self.repo_root / ".stegverse_runtime"
        self.state_path = self.runtime_dir / "state.json"
        self.receipts_path = self.runtime_dir / "action_receipts.json"

        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        with self.policy_path.open("r", encoding="utf-8") as fh:
            self.policy = json.load(fh)

        if not self.receipts_path.exists():
            self._save_receipts([])

    def _load_state(self) -> Dict[str, object]:
        with self.state_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _load_receipts(self) -> List[Dict[str, object]]:
        with self.receipts_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save_receipts(self, receipts: List[Dict[str, object]]) -> None:
        with self.receipts_path.open("w", encoding="utf-8") as fh:
            json.dump(receipts, fh, indent=2)

    def reset(self) -> None:
        self._save_receipts([])

    def available_actions(self) -> Dict[str, Dict[str, str]]:
        return self.policy["allowed_actions"]

    def _build_receipt(
        self,
        action_name: str,
        decision: str,
        reason: str,
        current_state: str,
        required_state: str,
        previous_receipt_id: str,
    ) -> ActionReceipt:
        timestamp_utc = datetime.now(timezone.utc).isoformat()

        material = json.dumps(
            {
                "action_name": action_name,
                "decision": decision,
                "reason": reason,
                "current_state": current_state,
                "required_state": required_state,
                "previous_receipt_id": previous_receipt_id,
                "timestamp_utc": timestamp_utc,
            },
            sort_keys=True,
        ).encode("utf-8")

        receipt_hash = hashlib.sha256(material).hexdigest()
        receipt_id = receipt_hash[:16].upper()

        return ActionReceipt(
            receipt_id=receipt_id,
            action_name=action_name,
            decision=decision,
            reason=reason,
            current_state=current_state,
            required_state=required_state,
            previous_receipt_id=previous_receipt_id,
            timestamp_utc=timestamp_utc,
            receipt_hash=receipt_hash,
        )

    def request_action(self, action_name: str) -> Dict[str, object]:
        state = self._load_state()
        receipts = self._load_receipts()

        current_state = state["current_state"]
        required_state = self.policy["admissible_runtime_state"]
        previous_receipt_id = receipts[-1]["receipt_id"] if receipts else "GENESIS"

        if action_name not in self.policy["allowed_actions"]:
            receipt = self._build_receipt(
                action_name=action_name,
                decision="DENIED",
                reason="unknown_action",
                current_state=current_state,
                required_state=required_state,
                previous_receipt_id=previous_receipt_id,
            )
            receipts.append(receipt.to_dict())
            self._save_receipts(receipts)
            return {
                "action_name": action_name,
                "decision": "DENIED",
                "reason": "unknown_action",
                "receipt": receipt.to_dict(),
            }

        if current_state != required_state:
            receipt = self._build_receipt(
                action_name=action_name,
                decision="DENIED",
                reason="inadmissible_runtime_state",
                current_state=current_state,
                required_state=required_state,
                previous_receipt_id=previous_receipt_id,
            )
            receipts.append(receipt.to_dict())
            self._save_receipts(receipts)
            return {
                "action_name": action_name,
                "decision": "DENIED",
                "reason": "inadmissible_runtime_state",
                "receipt": receipt.to_dict(),
            }

        receipt = self._build_receipt(
            action_name=action_name,
            decision="ALLOWED",
            reason="admissible_runtime_state",
            current_state=current_state,
            required_state=required_state,
            previous_receipt_id=previous_receipt_id,
        )
        receipts.append(receipt.to_dict())
        self._save_receipts(receipts)

        return {
            "action_name": action_name,
            "decision": "ALLOWED",
            "reason": "admissible_runtime_state",
            "receipt": receipt.to_dict(),
        }

    def receipt_chain(self) -> List[Dict[str, object]]:
        return self._load_receipts()

    def explain(self) -> Dict[str, object]:
        state = self._load_state()
        return {
            "policy_name": self.policy["policy_name"],
            "policy_version": self.policy["version"],
            "current_state": state["current_state"],
            "required_state": self.policy["admissible_runtime_state"],
            "available_actions": sorted(self.policy["allowed_actions"].keys()),
            "total_action_receipts": len(self._load_receipts()),
        }
