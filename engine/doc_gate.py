from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Dict, List


@dataclass
class Receipt:
    receipt_id: str
    step_id: str
    sequence: int
    previous_receipt_id: str
    state_before: str
    state_after: str
    unlocked_document: str
    timestamp_utc: str
    receipt_hash: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "receipt_id": self.receipt_id,
            "step_id": self.step_id,
            "sequence": self.sequence,
            "previous_receipt_id": self.previous_receipt_id,
            "state_before": self.state_before,
            "state_after": self.state_after,
            "unlocked_document": self.unlocked_document,
            "timestamp_utc": self.timestamp_utc,
            "receipt_hash": self.receipt_hash,
        }


class StegVerseGate:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.docs_dir = self.repo_root / "docs"
        self.workflow_path = self.repo_root / "workflow" / "manifest.json"
        self.runtime_dir = self.repo_root / ".stegverse_runtime"
        self.state_path = self.runtime_dir / "state.json"
        self.receipts_path = self.runtime_dir / "receipts.json"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

        with self.workflow_path.open("r", encoding="utf-8") as fh:
            self.workflow = json.load(fh)

        self.initial_state = self.workflow["initial_state"]
        self.states = self.workflow["states"]
        self.steps = self.workflow["steps"]
        self.doc_rules = self.workflow["documents"]

        if not self.state_path.exists():
            self.reset()

    def _load_state(self) -> Dict[str, object]:
        with self.state_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save_state(self, state: Dict[str, object]) -> None:
        with self.state_path.open("w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2)

    def _load_receipts(self) -> List[Dict[str, object]]:
        with self.receipts_path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _save_receipts(self, receipts: List[Dict[str, object]]) -> None:
        with self.receipts_path.open("w", encoding="utf-8") as fh:
            json.dump(receipts, fh, indent=2)

    def reset(self) -> None:
        state = {
            "current_state": self.initial_state,
            "completed_steps": [],
            "unlocked_documents": self._compute_unlocked_documents([]),
        }
        self._save_state(state)
        self._save_receipts([])

    def _compute_unlocked_documents(self, completed_steps: List[str]) -> List[str]:
        unlocked = []
        completed = set(completed_steps)
        for doc_name, rule in self.doc_rules.items():
            required = set(rule.get("required_steps", []))
            if required.issubset(completed):
                unlocked.append(doc_name)
        return sorted(unlocked)

    def status(self) -> Dict[str, object]:
        state = self._load_state()
        return {
            "current_state": state["current_state"],
            "completed_steps": state["completed_steps"],
            "unlocked_documents": state["unlocked_documents"],
            "total_receipts": len(self._load_receipts()),
        }

    def next_admissible_steps(self) -> List[str]:
        state = self._load_state()
        current_state = state["current_state"]
        completed = set(state["completed_steps"])
        available = []
        for step_id, step in self.steps.items():
            if step_id in completed:
                continue
            if step["from_state"] == current_state:
                available.append(step_id)
        return sorted(available)

    def describe_runtime(self) -> Dict[str, object]:
        state = self.status()
        return {
            "current_state": state["current_state"],
            "completed_steps": state["completed_steps"],
            "total_receipts": state["total_receipts"],
            "next_admissible_steps": self.next_admissible_steps(),
            "unlocked_documents": state["unlocked_documents"],
            "locked_documents": [
                name for name in sorted(self.doc_rules.keys())
                if name not in set(state["unlocked_documents"])
            ],
        }

    def list_documents(self) -> List[Dict[str, object]]:
        unlocked = set(self._load_state()["unlocked_documents"])
        return [
            {"document": doc_name, "path": f"docs/{doc_name}", "unlocked": doc_name in unlocked}
            for doc_name in sorted(self.doc_rules.keys())
        ]

    def bulk_retrieval_allowed(self) -> bool:
        return set(self._load_state()["unlocked_documents"]) == set(self.doc_rules.keys())

    def bulk_retrieval(self) -> Dict[str, str]:
        if not self.bulk_retrieval_allowed():
            raise PermissionError("Bulk retrieval denied: not all governed artifacts are unlocked.")
        return {
            item["document"]: (self.docs_dir / item["document"]).read_text(encoding="utf-8")
            for item in self.list_documents()
        }

    def retrieve_document(self, doc_name: str) -> str:
        state = self._load_state()
        if doc_name not in state["unlocked_documents"]:
            raise PermissionError(f"Access denied: {doc_name} is not yet unlocked by the workflow.")
        return (self.docs_dir / doc_name).read_text(encoding="utf-8")

    def run_step(self, step_id: str) -> Dict[str, object]:
        if step_id not in self.steps:
            raise KeyError(f"Unknown workflow step: {step_id}")

        state = self._load_state()
        receipts = self._load_receipts()
        step = self.steps[step_id]
        current_state = state["current_state"]
        required_state = step["from_state"]

        if current_state != required_state:
            raise ValueError(
                f"Step {step_id} is not admissible from state {current_state}. Expected {required_state}."
            )

        completed_steps = list(state["completed_steps"])
        if step_id in completed_steps:
            raise ValueError(f"Step {step_id} has already been completed.")

        completed_steps.append(step_id)
        next_state = step["to_state"]
        unlocked_documents = self._compute_unlocked_documents(completed_steps)

        previous_receipt_id = receipts[-1]["receipt_id"] if receipts else "GENESIS"
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        material = json.dumps(
            {
                "step_id": step_id,
                "sequence": len(receipts) + 1,
                "previous_receipt_id": previous_receipt_id,
                "state_before": current_state,
                "state_after": next_state,
                "unlocked_document": step["unlocks_document"],
                "timestamp_utc": timestamp_utc,
            },
            sort_keys=True,
        ).encode("utf-8")

        receipt_hash = hashlib.sha256(material).hexdigest()
        receipt_id = receipt_hash[:16].upper()

        receipt = Receipt(
            receipt_id=receipt_id,
            step_id=step_id,
            sequence=len(receipts) + 1,
            previous_receipt_id=previous_receipt_id,
            state_before=current_state,
            state_after=next_state,
            unlocked_document=step["unlocks_document"],
            timestamp_utc=timestamp_utc,
            receipt_hash=receipt_hash,
        )

        state["current_state"] = next_state
        state["completed_steps"] = completed_steps
        state["unlocked_documents"] = unlocked_documents
        receipts.append(receipt.to_dict())

        self._save_state(state)
        self._save_receipts(receipts)

        return {
            "step_id": step_id,
            "state_before": current_state,
            "state_after": next_state,
            "unlocked_document": step["unlocks_document"],
            "receipt": receipt.to_dict(),
        }

    def receipt_chain(self) -> List[Dict[str, object]]:
        return self._load_receipts()
