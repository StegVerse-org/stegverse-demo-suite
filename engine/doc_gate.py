from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
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
        return self.__dict__.copy()

class StegVerseGate:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.docs_dir = self.repo_root / "docs"
        self.workflow_path = self.repo_root / "workflow" / "manifest.json"
        self.runtime_dir = self.repo_root / ".stegverse_runtime"
        self.state_path = self.runtime_dir / "state.json"
        self.receipts_path = self.runtime_dir / "receipts.json"
        self.runtime_dir.mkdir(parents=True, exist_ok=True)
        self.workflow = json.loads(self.workflow_path.read_text(encoding="utf-8"))
        self.initial_state = self.workflow["initial_state"]
        self.steps = self.workflow["steps"]
        self.doc_rules = self.workflow["documents"]
        if not self.state_path.exists():
            self.reset()

    def _load_state(self): return json.loads(self.state_path.read_text(encoding="utf-8"))
    def _save_state(self, state): self.state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    def _load_receipts(self): return json.loads(self.receipts_path.read_text(encoding="utf-8"))
    def _save_receipts(self, receipts): self.receipts_path.write_text(json.dumps(receipts, indent=2), encoding="utf-8")

    def reset(self):
        state = {"current_state": self.initial_state, "completed_steps": [], "unlocked_documents": self._compute_unlocked_documents([])}
        self._save_state(state); self._save_receipts([])

    def _compute_unlocked_documents(self, completed_steps: List[str]) -> List[str]:
        completed = set(completed_steps)
        return sorted([doc for doc, rule in self.doc_rules.items() if set(rule.get("required_steps", [])).issubset(completed)])

    def status(self):
        s = self._load_state()
        return {"current_state": s["current_state"], "completed_steps": s["completed_steps"], "unlocked_documents": s["unlocked_documents"], "total_receipts": len(self._load_receipts())}

    def next_admissible_steps(self) -> List[str]:
        s = self._load_state(); current = s["current_state"]; completed = set(s["completed_steps"])
        return sorted([step_id for step_id, step in self.steps.items() if step_id not in completed and step["from_state"] == current])

    def describe_runtime(self):
        st = self.status()
        return {
            "current_state": st["current_state"],
            "completed_steps": st["completed_steps"],
            "total_receipts": st["total_receipts"],
            "next_admissible_steps": self.next_admissible_steps(),
            "unlocked_documents": st["unlocked_documents"],
            "locked_documents": [d for d in sorted(self.doc_rules) if d not in set(st["unlocked_documents"])],
        }

    def list_documents(self):
        unlocked = set(self._load_state()["unlocked_documents"])
        return [{"document": d, "path": f"docs/{d}", "unlocked": d in unlocked} for d in sorted(self.doc_rules)]

    def bulk_retrieval(self):
        if set(self._load_state()["unlocked_documents"]) != set(self.doc_rules):
            raise PermissionError("Bulk retrieval denied: not all governed artifacts are unlocked.")
        return {item["document"]: (self.docs_dir / item["document"]).read_text(encoding="utf-8") for item in self.list_documents()}

    def retrieve_document(self, doc_name: str) -> str:
        if doc_name not in self._load_state()["unlocked_documents"]:
            raise PermissionError(f"Access denied: {doc_name} is not yet unlocked by the workflow.")
        return (self.docs_dir / doc_name).read_text(encoding="utf-8")

    def run_step(self, step_id: str):
        if step_id not in self.steps: raise KeyError(f"Unknown workflow step: {step_id}")
        state = self._load_state(); receipts = self._load_receipts(); step = self.steps[step_id]
        current = state["current_state"]
        if current != step["from_state"]:
            raise ValueError(f"Step {step_id} is not admissible from state {current}. Expected {step['from_state']}.")
        completed = list(state["completed_steps"])
        if step_id in completed: raise ValueError(f"Step {step_id} has already been completed.")
        completed.append(step_id); next_state = step["to_state"]; unlocked = self._compute_unlocked_documents(completed)
        previous_receipt_id = receipts[-1]["receipt_id"] if receipts else "GENESIS"
        timestamp_utc = datetime.now(timezone.utc).isoformat()
        material = json.dumps({"step_id": step_id, "sequence": len(receipts)+1, "previous_receipt_id": previous_receipt_id, "state_before": current, "state_after": next_state, "unlocked_document": step["unlocks_document"], "timestamp_utc": timestamp_utc}, sort_keys=True).encode("utf-8")
        receipt_hash = hashlib.sha256(material).hexdigest(); receipt_id = receipt_hash[:16].upper()
        receipt = Receipt(receipt_id, step_id, len(receipts)+1, previous_receipt_id, current, next_state, step["unlocks_document"], timestamp_utc, receipt_hash)
        state["current_state"] = next_state; state["completed_steps"] = completed; state["unlocked_documents"] = unlocked
        receipts.append(receipt.to_dict()); self._save_state(state); self._save_receipts(receipts)
        return {"step_id": step_id, "state_before": current, "state_after": next_state, "unlocked_document": step["unlocks_document"], "receipt": receipt.to_dict()}

    def receipt_chain(self): return self._load_receipts()
