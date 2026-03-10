# StegVerse Demo Suite

This repository demonstrates a **governed artifact workflow** where execution receipts advance system state and unlock controlled artifacts.

The demo illustrates how a system can enforce **admissible state transitions** using execution receipts as governance primitives.

Each demo step produces a receipt that validates the transition to the next state. Documents remain inaccessible until the required execution step completes.

The system demonstrates a simple governance model:

execution → receipt → admissible state transition → artifact unlock

---

# Repository Structure

stegverse-demo-suite/
├─ README.md
├─ docs/
│  ├─ RUN_DEMO_INSTRUCTIONS.md
│  ├─ doc1_demo1.md
│  ├─ doc2_demo2.md
│  ├─ doc3_demo3.md
│  ├─ doc4_demo4.md
│  └─ doc5_system_summary.md
├─ engine/
│  ├─ doc_gate.py
│  ├─ run_demo.py
│  └─ stegverse_cli.py
└─ workflow/
   └─ manifest.json

---

# Architecture Overview

workflow execution
        ↓
receipt generation
        ↓
state validation
        ↓
artifact unlock

Each step produces a receipt that validates the system's progression to the next admissible state.

---

# Running the Demo

Follow the instructions in:

docs/RUN_DEMO_INSTRUCTIONS.md

Or run directly from the repository root:

python engine/run_demo.py

---

# Expected Behavior

Running the demo demonstrates that:

- execution receipts are generated for each workflow step
- governed artifacts unlock only after valid execution
- the workflow progresses through admissible state transitions
- the final system summary remains accessible after completion

---

# Purpose

This repository is a minimal demonstration of **execution-governed artifact access**.

It shows how receipts generated during computation can act as governance primitives that control system state and artifact availability.
