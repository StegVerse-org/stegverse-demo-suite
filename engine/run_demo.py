from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CLI = BASE_DIR / "stegverse_cli.py"

DEMO_SEQUENCE = ["demo1", "demo2", "demo3", "demo4"]
DOC_SEQUENCE = ["doc2", "doc3", "doc4", "doc5"]


def run_cli(*args: str) -> int:
    cmd = [sys.executable, str(CLI), *args]
    result = subprocess.run(cmd, cwd=BASE_DIR)
    return result.returncode


def main() -> None:
    print("\nStegVerse Demo Suite — Full Workflow Run\n")

    if not CLI.exists():
        print("Missing stegverse_cli.py in repo root.")
        print("Place this file next to run_demo.py and try again.")
        sys.exit(1)

    print("Initial status:\n")
    run_cli("status")
    print("\nAttempting bulk retrieval before demos:\n")
    run_cli("retrieve-all")

    for demo, next_doc in zip(DEMO_SEQUENCE, DOC_SEQUENCE):
        print(f"\n=== Running {demo} ===\n")
        code = run_cli("run", demo)
        if code != 0:
            print(f"{demo} failed with exit code {code}")
            sys.exit(code)

        print(f"\n=== Retrieving {next_doc} ===\n")
        run_cli("retrieve", next_doc)

    print("\n=== Final Status ===\n")
    run_cli("status")

    print("\n=== Receipt Chain ===\n")
    run_cli("receipts")

    print("\n=== Final Bulk Retrieval Check ===\n")
    run_cli("retrieve-all")

    print("\nStegVerse full workflow run complete.\n")


if __name__ == "__main__":
    main()
