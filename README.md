# StegVerse Demo Suite

A compact research prototype demonstrating a governed artifact workflow in which
execution receipts advance system state and unlock controlled artifacts.

The suite illustrates a simple but extensible governance model:

**execution -> receipt -> admissible state transition -> artifact unlock**

Each demo step produces a receipt that validates progression to the next admissible
state. Until the required execution step completes, downstream artifacts remain inaccessible.

---

## Core Idea

This repository shows how receipts generated during computation can function as
governance primitives.

Rather than treating execution as an isolated event, the system uses execution evidence
to determine:

- whether the workflow may advance
- whether the next artifact may be revealed
- whether the resulting state is admissible

This makes the demo a compact illustration of execution-governed artifact access.

---

## StegVerse Runtime Interface

This version is designed to be operated through a **StegVerse-first runtime wrapper**
rather than through raw Python entrypoints.

Preferred commands from the repository root:

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

Legacy Python entrypoints still work:

```bash
python engine/run_demo.py
python engine/stegverse_cli.py status
```

Conceptually:

```text
StegVerse command
        |
        v
CLI interpreter
        |
        v
receipt-backed workflow engine
        |
        v
governed artifacts
```
---

This version adds **cross-platform launchers** so StegVerse can be run directly on:

- Linux / macOS / Git Bash: `./stegverse`
- Windows Command Prompt / PowerShell: `stegverse.cmd`

## Quick start

### Unix-like shells
```bash
chmod +x stegverse
./stegverse help
./stegverse explain
./stegverse demo
```

### Windows
```powershell
stegverse.cmd help
stegverse.cmd explain
stegverse.cmd demo
```

### Python fallback
```bash
python engine/run_demo.py
python engine/stegverse_cli.py status
```

---

## Repository Structure

```text
stegverse-demo-suite/
|-- README.md
|-- stegverse
|-- docs/
|   |-- RUN_DEMO_INSTRUCTIONS.md
|   |-- doc1_demo1.md
|   |-- doc2_demo2.md
|   |-- doc3_demo3.md
|   |-- doc4_demo4.md
|   `-- doc5_system_summary.md
|-- engine/
|   |-- doc_gate.py
|   |-- run_demo.py
|   `-- stegverse_cli.py
`-- workflow/
    `-- manifest.json
```

### docs/
Governed artifacts and walkthrough materials that unlock progressively as the workflow advances.

### engine/
Runtime components responsible for execution, receipt generation, and governance enforcement.

### workflow/
Workflow definitions and state progression metadata.

### stegverse
Root command wrapper that makes the demo feel like a StegVerse runtime interface.

---

## Recommended Flow

From the repository root:

```bash
./stegverse reset
./stegverse explain
./stegverse demo
./stegverse explain
./stegverse receipts
```

For step-by-step exploration:

```bash
./stegverse reset
./stegverse explain
./stegverse run demo1
./stegverse explain
./stegverse run demo2
./stegverse explain
```

---

## Architecture Overview

```text
workflow execution
        |
        v
receipt generation
        |
        v
state validation
        |
        v
artifact unlock
```

A successful execution step produces a receipt. That receipt validates the next
admissible transition, which in turn unlocks the next governed artifact.

---

## Expected Behavior

Running the demo should show that:

- execution receipts are generated for each workflow step
- governed artifacts unlock only after valid execution
- the workflow progresses through admissible state transitions
- the final system summary remains accessible after completion

---

## Why This Matters

Although intentionally small, the demo models a pattern that can be extended to:

- governed workflow orchestration
- controlled document or data release
- verifiable execution pipelines
- decentralized compute and policy-bound runtime systems

In that sense, the repository is not just a document demo. It is a compact illustration of how execution evidence can be used to govern system state.
