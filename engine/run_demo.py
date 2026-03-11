from __future__ import annotations

import sys
from pathlib import Path
from pprint import pformat

ENGINE_DIR = Path(__file__).resolve().parent
REPO_ROOT = ENGINE_DIR.parent
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))

from doc_gate import StegVerseGate  # noqa: E402
from actions.action_gate import ActionGate  # noqa: E402


def divider(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    gate = StegVerseGate(REPO_ROOT)
    action_gate = ActionGate(REPO_ROOT)

    divider("RESETTING RUNTIME")
    gate.reset()
    action_gate.reset()
    print("Runtime reset complete.")

    divider("INITIAL STATUS")
    print(pformat(gate.status(), sort_dicts=False))

    divider("PRE-WORKFLOW ACTION CHECK")
    print(action_gate.request_action("deploy_change")["message"])

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
    print(pformat(gate.describe_runtime(), sort_dicts=False))

    divider("POST-WORKFLOW ACTION CHECK")
    print(action_gate.request_action("deploy_change")["message"])

    divider("WORKFLOW RECEIPT CHAIN")
    for r in gate.receipt_chain():
        print(
            f"{r['sequence']}. {r['step_id']} | {r['receipt_id']} | "
            f"prev={r['previous_receipt_id']} | state={r['state_before']}->{r['state_after']}"
        )

    divider("ACTION RECEIPT CHAIN")
    for r in action_gate.action_receipt_chain():
        print(
            f"{r['sequence']}. {r['action_name']} | {r['action_receipt_id']} | "
            f"prev={r['previous_action_receipt_id']} | decision={r['decision']} | state={r['current_state']}"
        )

    divider("FINAL BULK RETRIEVAL CHECK")
    artifacts = gate.bulk_retrieval()
    print(f"Bulk retrieval allowed. Retrieved {len(artifacts)} governed artifacts.")

    divider("DEMO COMPLETE")
    print("StegVerse governed workflow and action gate executed successfully.")


if __name__ == "__main__":
    main()
