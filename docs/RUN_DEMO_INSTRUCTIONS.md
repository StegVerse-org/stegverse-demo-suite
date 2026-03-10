# run_demo.py Wrapper

Place `run_demo.py` in the `engine/` directory of the `stegverse-demo-suite` repository.

Expected location:

```text
stegverse-demo-suite/engine/run_demo.py
```

## Purpose

This wrapper executes the full StegVerse governed artifact workflow end-to-end.

## What It Does

The script automatically performs the following sequence:

1. Displays the initial runtime status
2. Attempts bulk retrieval before any demos complete
3. Runs Demo 1 and unlocks Doc 2
4. Runs Demo 2 and unlocks Doc 3
5. Runs Demo 3 and unlocks Doc 4
6. Runs Demo 4 and unlocks Doc 5
7. Displays final runtime status
8. Prints the full receipt chain
9. Performs a final bulk retrieval verification

## Command

Run the demo from the repository root:

```bash
python engine/run_demo.py
```

## Expected Result

The script demonstrates that:

- receipts are generated for each workflow step
- documents unlock as governed artifacts
- the workflow progresses through admissible state transitions
- the final system summary remains accessible after completion

## Conceptual Flow

```text
execution
   |
   v
receipt
   |
   v
admissible state transition
   |
   v
artifact unlock
```
