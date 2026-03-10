# StegVerse Runtime Commands

This repo can be operated through the root `stegverse` wrapper so the end user
interacts with StegVerse directly rather than calling Python manually.

## Preferred Usage

From the repository root:

```bash
./stegverse help
./stegverse explain
./stegverse status
./stegverse list
./stegverse tree
./stegverse run demo1
./stegverse get doc2_demo2.md
./stegverse receipts
./stegverse bulk
./stegverse reset
./stegverse demo
```

## Best Quick Start

```bash
./stegverse reset
./stegverse explain
./stegverse demo
./stegverse explain
./stegverse receipts
```

## Stepwise Exploration

```bash
./stegverse reset
./stegverse explain
./stegverse run demo1
./stegverse explain
./stegverse run demo2
./stegverse explain
./stegverse run demo3
./stegverse explain
./stegverse run demo4
./stegverse explain
```

## Unix-like shells
```bash
./stegverse help
./stegverse explain
./stegverse tree
./stegverse demo
```

## Windows
```powershell
stegverse.cmd help
stegverse.cmd explain
stegverse.cmd tree
stegverse.cmd demo
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

## What `./stegverse explain` Does

It prints a human-friendly runtime view, for example:

```text
StegVerse Runtime
----------------------------------------
current state: state2
completed steps: demo1 demo2
receipts: 2

next admissible steps:
 - demo3

unlocked artifacts:
 - doc1_demo1.md
 - doc2_demo2.md
 - doc3_demo3.md
```

## Python Fallback

If needed, the original Python entrypoints still work:

```bash
python engine/run_demo.py
python engine/stegverse_cli.py status
```
