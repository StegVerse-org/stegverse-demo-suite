# StegVerse Runtime Commands

This repo can now be operated through the root `stegverse` wrapper so the end user
interacts with StegVerse directly rather than calling Python manually.

## Preferred Usage

From the repository root:

```bash
./stegverse status
./stegverse list
./stegverse run demo1
./stegverse get doc2_demo2.md
./stegverse receipts
./stegverse bulk
./stegverse reset
./stegverse demo
```

## Demo Command

To run the full governed workflow end-to-end:

```bash
./stegverse demo
```

## Python Fallback

If needed, the original Python entrypoints still work:

```bash
python engine/run_demo.py
python engine/stegverse_cli.py status
```

## What `./stegverse demo` Does

The wrapper automatically performs the following sequence:

1. Displays the initial runtime status
2. Attempts bulk retrieval before any demos complete
3. Runs Demo 1 and unlocks Doc 2
4. Runs Demo 2 and unlocks Doc 3
5. Runs Demo 3 and unlocks Doc 4
6. Runs Demo 4 and unlocks Doc 5
7. Displays final runtime status
8. Prints the full receipt chain
9. Performs a final bulk retrieval verification
