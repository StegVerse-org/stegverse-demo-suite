from __future__ import annotations

from pathlib import Path
from pprint import pformat
from doc_gate import StegVerseGate


def divider(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    gate = StegVerseGate(repo_root)

    divider("RESETTING RUNTIME")
    gate.reset()
    print("Runtime reset complete.")

    divider("INITIAL STATUS")
    print(pformat(gate.status(), sort_dicts=False))

    divider("INITIAL BULK RETRIEVAL CHECK")
    try:
        gate.bulk_retrieval()
        print("Unexpected success.")
    except PermissionError as exc:
        print(f"Expected denial: {exc}")

    for step_id in ("demo1", "demo2", "demo3", "demo4"):
        divider(f"RUNNING {step_id.upper()}")
        result = gate.run_step(step_id)
        print(f"State transition: {result['state_before']} -> {result['state_after']}")
        print(f"Unlocked document: {result['unlocked_document']}")
        print("Receipt summary:")
        print(
            pformat(
                {
                    "receipt_id": result["receipt"]["receipt_id"],
                    "sequence": result["receipt"]["sequence"],
                    "previous_receipt_id": result["receipt"]["previous_receipt_id"],
                    "receipt_hash": result["receipt"]["receipt_hash"],
                },
                sort_dicts=False,
            )
        )

    divider("FINAL STATUS")
    print(pformat(gate.status(), sort_dicts=False))

    divider("RUNTIME EXPLANATION")
    explanation = gate.describe_runtime()
    print(pformat(explanation, sort_dicts=False))

    divider("RECEIPT CHAIN")
    for receipt in gate.receipt_chain():
        print(
            f"{receipt['sequence']}. {receipt['step_id']} | "
            f"{receipt['receipt_id']} | prev={receipt['previous_receipt_id']} | "
            f"state={receipt['state_before']}->{receipt['state_after']}"
        )

    divider("FINAL BULK RETRIEVAL CHECK")
    artifacts = gate.bulk_retrieval()
    print(f"Bulk retrieval allowed. Retrieved {len(artifacts)} governed artifacts.")
    print("Artifacts:")
    for name in sorted(artifacts):
        print(f"- {name}")

    divider("DEMO COMPLETE")
    print("StegVerse governed workflow executed successfully.")


if __name__ == "__main__":
    main()
