from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = BASE_DIR / "docs"
STATE_DIR = BASE_DIR / "state"
STATE_DIR.mkdir(exist_ok=True)

STATE_FILE = STATE_DIR / "workflow_state.json"

DOC_MAP = {
    "doc1": "doc1_demo1.md",
    "doc2": "doc2_demo2.md",
    "doc3": "doc3_demo3.md",
    "doc4": "doc4_demo4.md",
    "doc5": "doc5_system_summary.md",
}

REQUIREMENTS = {
    "doc1": [],
    "doc2": ["demo1"],
    "doc3": ["demo2"],
    "doc4": ["demo3"],
    "doc5": ["demo1", "demo2", "demo3", "demo4"],
}

TTL_SECONDS = {
    "doc1": None,
    "doc2": 60,
    "doc3": 60,
    "doc4": 60,
    "doc5": None,
}

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _default_state() -> Dict:
    return {
        "completed": {},
        "receipts": [],
        "doc5_unlocked": False,
    }

def load_state() -> Dict:
    if not STATE_FILE.exists():
        return _default_state()
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))

def save_state(state: Dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")

def mark_demo_complete(demo_name: str, receipt_id: str) -> None:
    state = load_state()
    state["completed"][demo_name] = {
        "receipt_id": receipt_id,
        "completed_at": _now().isoformat(),
    }
    state["receipts"].append(receipt_id)
    if all(step in state["completed"] for step in ("demo1", "demo2", "demo3", "demo4")):
        state["doc5_unlocked"] = True
    save_state(state)

def _is_fresh(iso_ts: str, ttl_seconds: int) -> bool:
    ts = datetime.fromisoformat(iso_ts)
    return (_now() - ts) <= timedelta(seconds=ttl_seconds)

def can_access(doc_id: str) -> Tuple[bool, str]:
    state = load_state()

    if doc_id not in DOC_MAP:
        return False, "document.unknown"

    reqs = REQUIREMENTS[doc_id]
    for req in reqs:
        if req not in state["completed"]:
            return False, "dependency.unsatisfied"

    ttl = TTL_SECONDS[doc_id]
    if ttl is None:
        if doc_id == "doc5" and not state.get("doc5_unlocked", False):
            return False, "workflow.incomplete"
        return True, "ok"

    # time-bound docs depend on most recent required step freshness
    if reqs:
        latest_req = reqs[-1]
        completed_at = state["completed"][latest_req]["completed_at"]
        if not _is_fresh(completed_at, ttl):
            return False, "receipt.expired"

    return True, "ok"

def retrieve_document(doc_id: str) -> Tuple[bool, str, str]:
    allowed, reason = can_access(doc_id)
    if not allowed:
        return False, reason, ""
    filename = DOC_MAP[doc_id]
    content = (DOCS_DIR / filename).read_text(encoding="utf-8")
    return True, "ok", content

def retrieve_all_documents() -> Dict[str, Dict[str, str]]:
    result = {}
    for doc_id in DOC_MAP:
        allowed, reason = can_access(doc_id)
        result[doc_id] = {
            "allowed": str(allowed).lower(),
            "reason": reason,
            "file": DOC_MAP[doc_id],
        }
    return result
