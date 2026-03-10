import os
import time
from engine.policy_engine import check_access
from engine.receipt_engine import generate_receipt
from engine.doc_gate import retrieve_document

def run_demo():
    print("\nStegVerse Demo Suite\n")

    demos = ["demo1", "demo2", "demo3", "demo4"]

    for demo in demos:
        print(f"\nRunning {demo}")

        allowed, reason = check_access(demo)

        if not allowed:
            print(f"Access denied: {reason}")
            return

        receipt = generate_receipt(demo)
        print(f"Receipt generated: {receipt}")

        next_doc = retrieve_document(demo)
        print(f"Unlocked document: {next_doc}")

        time.sleep(1)

    print("\nAll demos complete.")
    print("Final document unlocked: doc5_system_summary.md")

if __name__ == "__main__":
    run_demo()
