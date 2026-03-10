from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pformat
import subprocess
import sys

from doc_gate import StegVerseGate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StegVerse governed artifact workflow CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("list")
    sub.add_parser("bulk")
    sub.add_parser("receipts")
    sub.add_parser("reset")
    sub.add_parser("demo")
    run = sub.add_parser("run")
    run.add_argument("step_id")
    get_doc = sub.add_parser("get")
    get_doc.add_argument("document")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    gate = StegVerseGate(repo_root)

    if args.command == "status":
        print(pformat(gate.status(), sort_dicts=False))
        return
    if args.command == "list":
        for item in gate.list_documents():
            mark = "UNLOCKED" if item["unlocked"] else "LOCKED"
            print(f"{mark:8} {item['document']}  ({item['path']})")
        return
    if args.command == "bulk":
        try:
            artifacts = gate.bulk_retrieval()
            print(f"Retrieved {len(artifacts)} documents.")
            for name in sorted(artifacts):
                print(f"- {name}")
        except Exception as exc:
            print(exc)
        return
    if args.command == "receipts":
        receipts = gate.receipt_chain()
        if not receipts:
            print("No receipts yet.")
            return
        for receipt in receipts:
            print(f"{receipt['sequence']}. {receipt['step_id']} | {receipt['receipt_id']} | prev={receipt['previous_receipt_id']}")
        return
    if args.command == "reset":
        gate.reset()
        print("Runtime reset complete.")
        return
    if args.command == "run":
        try:
            print(pformat(gate.run_step(args.step_id), sort_dicts=False))
        except Exception as exc:
            print(f"Run failed: {exc}")
        return
    if args.command == "get":
        try:
            print(gate.retrieve_document(args.document))
        except Exception as exc:
            print(f"Retrieval failed: {exc}")
        return
    if args.command == "demo":
        result = subprocess.run([sys.executable, str(repo_root / "engine" / "run_demo.py")], cwd=str(repo_root), check=False)
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
