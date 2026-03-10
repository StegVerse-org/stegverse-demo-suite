# run_demo.py Wrapper

Place `run_demo.py` in the `engine/` folder of the `stegverse-demo-suite` repository.

Expected location:

stegverse-demo-suite/engine/run_demo.py

## What it does

This wrapper runs the full governed demo workflow automatically:

1. Shows initial runtime status
2. Attempts bulk retrieval before any demos complete
3. Runs Demo 1 → retrieves Doc 2
4. Runs Demo 2 → retrieves Doc 3
5. Runs Demo 3 → retrieves Doc 4
6. Runs Demo 4 → retrieves Doc 5
7. Shows final status
8. Prints receipt chain
9. Performs a final bulk retrieval check

## Command

```bash
python engine/run_demo.py
