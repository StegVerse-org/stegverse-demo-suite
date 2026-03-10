from __future__ import annotations

import argparse
import json
import random
from datetime import datetime, timezone
from pathlib import Path

from engine.doc_gate import load_state, mark_demo_complete, retrieve_all_documents, retrieve_document

BASE_DIR = Path(__file__).resolve().parent
RECEIPTS_DIR = BASE_DIR / "receipts"
RECEIPTS_DIR.mkdir(exist_ok=True)

DEMO_TO_DOC = {
    "demo1": "doc2",
    "demo2": "doc3",
    "demo3": "doc4",
    "demo4": "doc5",
}

def _make_receipt_id(demo_name: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rand = random.randint(1000, 9999)
    return f"r-{demo_name}-{stamp}-{rand}"

def _write_receipt(demo_name: str, receipt_id: str) -> Path:
    path = RECEIPTS_DIR / f"{receipt_id}.json"
    payload = {
        "receipt_id": receipt_id,
        "demo": demo_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "completed",
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path

def cmd_status() -> None:
    state = load_state()
    completed = state.get("completed", {})
    print("StegVerse Runtime Status")
    print()
    print("Completed demos:", len(completed))
    if completed:
        for demo_name, meta in completed.items():
            print(f"  - {demo_name}: {meta['receipt_id']}")
    else:
        print("  - none yet")
    print()
    print("Doc5 unlocked:", state.get("doc5_unlocked", False))

def cmd_receipts() -> None:
    files = sorted(RECEIPTS_DIR.glob("*.json"))
    print("Receipt Chain")
    print()
    if not files:
        print("No receipts found.")
        return
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        print(f"{data['receipt_id']} -> {data['demo']}")

def cmd_run(demo_name: str) -> None:
    if demo_name not in ("demo1", "demo2", "demo3", "demo4"):
        print(f"Unknown demo: {demo_name}")
        return

    receipt_id = _make_receipt_id(demo_name)
    receipt_path = _write_receipt(demo_name, receipt_id)
    mark_demo_complete(demo_name, receipt_id)

    print(f"Running {demo_name}")
    print(f"Receipt generated: {receipt_id}")
    print(f"Receipt saved: {receipt_path}")

    next_doc = DEMO_TO_DOC.get(demo_name)
    if next_doc:
        ok, reason, _content = retrieve_document(next_doc)
        if ok:
            print(f"Unlocked document: {next_doc}")
        else:
            print(f"Next document blocked: {next_doc} ({reason})")

def cmd_retrieve(doc_id: str) -> None:
    ok, reason, content = retrieve_document(doc_id)
    if not ok:
        print("Access denied")
        print(f"Reason: {reason}")
        return
    print(content)

def cmd_retrieve_all() -> None:
    result = retrieve_all_documents()
    print(json.dumps(result, indent=2))

def main() -> None:
    parser = argparse.ArgumentParser(prog="stegverse", description="StegVerse demo runtime CLI")
    sub = parser.add_subparsers(dest="command")

    run = sub.add_parser("run", help="Run an individual demo")
    run.add_argument("demo", help="demo1 | demo2 | demo3 | demo4")

    retrieve = sub.add_parser("retrieve", help="Retrieve a governed document")
    retrieve.add_argument("doc", help="doc1 | doc2 | doc3 | doc4 | doc5")

    sub.add_parser("retrieve-all", help="Attempt retrieval of all documents")
    sub.add_parser("status", help="Show workflow state")
    sub.add_parser("receipts", help="Show receipt chain")

    args = parser.parse_args()

    if args.command == "run":
        cmd_run(args.demo)
    elif args.command == "retrieve":
        cmd_retrieve(args.doc)
    elif args.command == "retrieve-all":
        cmd_retrieve_all()
    elif args.command == "status":
        cmd_status()
    elif args.command == "receipts":
        cmd_receipts()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()