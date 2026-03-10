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

    sub.add_parser("help", help="Show StegVerse command guidance")
    sub.add_parser("status", help="Show runtime status")
    sub.add_parser("list", help="List artifacts and lock state")
    sub.add_parser("tree", help="Show a compact runtime tree view")
    sub.add_parser("bulk", help="Attempt bulk retrieval")
    sub.add_parser("receipts", help="Show receipt chain")
    sub.add_parser("reset", help="Reset runtime state")
    sub.add_parser("demo", help="Run the full end-to-end demo")
    sub.add_parser("explain", help="Show a human-friendly runtime explanation")

    run = sub.add_parser("run", help="Run a workflow step")
    run.add_argument("step_id")

    get_doc = sub.add_parser("get", help="Retrieve a specific document")
    get_doc.add_argument("document")

    return parser


def print_help_screen() -> None:
    print("StegVerse Runtime")
    print("-" * 40)
    print("Available commands:")
    print("  ./stegverse explain")
    print("  ./stegverse status")
    print("  ./stegverse list")
    print("  ./stegverse tree")
    print("  ./stegverse run demo1")
    print("  ./stegverse get doc2_demo2.md")
    print("  ./stegverse receipts")
    print("  ./stegverse bulk")
    print("  ./stegverse reset")
    print("  ./stegverse demo")
    print("")
    print("Recommended first steps:")
    print("  ./stegverse reset")
    print("  ./stegverse explain")
    print("  ./stegverse demo")


def explain_runtime(gate: StegVerseGate) -> None:
    status = gate.describe_runtime()
    print("\nStegVerse Runtime")
    print("-" * 40)
    print(f"current state: {status['current_state']}")
    steps = status["completed_steps"]
    print("completed steps:", " ".join(steps) if steps else "none")
    print(f"receipts: {status['total_receipts']}")
    print("")
    print("next admissible steps:")
    next_steps = status["next_admissible_steps"]
    if next_steps:
        for step in next_steps:
            print(f" - {step}")
    else:
        print(" - none")
    print("")
    print("unlocked artifacts:")
    for doc in status["unlocked_documents"]:
        print(f" - {doc}")
    if not status["unlocked_documents"]:
        print(" - none")
    print("")
    print("locked artifacts:")
    for doc in status["locked_documents"]:
        print(f" - {doc}")
    if not status["locked_documents"]:
        print(" - none")
    print("")


def print_tree(gate: StegVerseGate) -> None:
    status = gate.describe_runtime()
    print("StegVerse")
    print("|-- state:", status["current_state"])
    print("|-- receipts:", status["total_receipts"])
    print("|-- completed_steps")
    if status["completed_steps"]:
        for step in status["completed_steps"]:
            print("|   |--", step)
    else:
        print("|   `-- none")
    print("|-- next_admissible_steps")
    if status["next_admissible_steps"]:
        for step in status["next_admissible_steps"]:
            print("|   |--", step)
    else:
        print("|   `-- none")
    print("`-- artifacts")
    docs = gate.list_documents()
    for i, item in enumerate(docs):
        branch = "|--" if i < len(docs) - 1 else "`--"
        state = "UNLOCKED" if item["unlocked"] else "LOCKED"
        print(f"    {branch} {item['document']} [{state}]")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    repo_root = Path(__file__).resolve().parents[1]
    gate = StegVerseGate(repo_root)

    if args.command == "help":
        print_help_screen()
        return

    if args.command == "status":
        print(pformat(gate.status(), sort_dicts=False))
        return

    if args.command == "list":
        for item in gate.list_documents():
            mark = "UNLOCKED" if item["unlocked"] else "LOCKED"
            print(f"{mark:8} {item['document']}  ({item['path']})")
        return

    if args.command == "tree":
        print_tree(gate)
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

    if args.command == "explain":
        explain_runtime(gate)
        return

    if args.command == "demo":
        result = subprocess.run(
            [sys.executable, str(repo_root / "engine" / "run_demo.py")],
            cwd=str(repo_root),
            check=False,
        )
        raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
