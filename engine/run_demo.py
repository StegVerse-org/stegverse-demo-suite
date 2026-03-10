from __future__ import annotations
from pathlib import Path
from pprint import pformat
from doc_gate import StegVerseGate

def divider(title: str):
    print("\n" + "="*72); print(title); print("="*72)

def main():
    repo_root = Path(__file__).resolve().parents[1]
    gate = StegVerseGate(repo_root)
    divider("RESETTING RUNTIME"); gate.reset(); print("Runtime reset complete.")
    divider("INITIAL STATUS"); print(pformat(gate.status(), sort_dicts=False))
    divider("INITIAL BULK RETRIEVAL CHECK")
    try:
        gate.bulk_retrieval(); print("Unexpected success.")
    except PermissionError as exc:
        print(f"Expected denial: {exc}")
    for step_id in ("demo1","demo2","demo3","demo4"):
        divider(f"RUNNING {step_id.upper()}")
        result = gate.run_step(step_id)
        print(f"State transition: {result['state_before']} -> {result['state_after']}")
        print(f"Unlocked document: {result['unlocked_document']}")
    divider("FINAL STATUS"); print(pformat(gate.status(), sort_dicts=False))
    divider("RUNTIME EXPLANATION"); print(pformat(gate.describe_runtime(), sort_dicts=False))
    divider("RECEIPT CHAIN")
    for r in gate.receipt_chain():
        print(f"{r['sequence']}. {r['step_id']} | {r['receipt_id']} | prev={r['previous_receipt_id']} | state={r['state_before']}->{r['state_after']}")
    divider("FINAL BULK RETRIEVAL CHECK")
    artifacts = gate.bulk_retrieval()
    print(f"Bulk retrieval allowed. Retrieved {len(artifacts)} governed artifacts.")
    divider("DEMO COMPLETE"); print("StegVerse governed workflow executed successfully.")
if __name__ == "__main__":
    main()
