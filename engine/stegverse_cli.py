"""
Simple CLI for the StegVerse Demo Suite.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from pprint import pformat

from doc_gate import StegVerseGate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="StegVerse governed artifact workflow CLI"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show current runtime status")
    sub.add_parser("list", help="List governed artifacts and unlock status")
    sub.add_parser("bulk", help="Attempt bulk retrieval")
    sub.add_parser("receipts", help="Show the receipt chain")
    sub.add_parser("reset", help="Reset runtime state")

    run = sub.add_parser("run", help="Run a workflow step")
    run.add_argument("step_id", help="Workflow step id, for example: demo1")

    get_doc = sub.add_parser("get", help="Retrieve a specific document")
    get_doc.add_argument("document", help="Document filename, for example: doc2_demo2.md")

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
        except PermissionError as exc:
            print(exc)
            return
        print(f"Retrieved {len(artifacts)} documents.")
        for name in sorted(artifacts.keys()):
            print(f"- {name}")
        return

    if args.command == "receipts":
        receipts = gate.receipt_chain()
        if not receipts:
            print("No receipts yet.")
            return
        for receipt in receipts:
            print(
                f"{receipt['sequence']}. {receipt['step_id']} | "
                f"{receipt['receipt_id']} | prev={receipt['previous_receipt_id']}"
            )
        return

    if args.command == "reset":
        gate.reset()
        print("Runtime reset complete.")
        return

    if args.command == "run":
        try:
            result = gate.run_step(args.step_id)
        except Exception as exc:  # noqa: BLE001
            print(f"Run failed: {exc}")
            return
        print(pformat(result, sort_dicts=False))
        return

    if args.command == "get":
        try:
            print(gate.retrieve_document(args.document))
        except Exception as exc:  # noqa: BLE001
            print(f"Retrieval failed: {exc}")
        return


if __name__ == "__main__":
    main()
