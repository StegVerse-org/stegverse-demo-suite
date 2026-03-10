# StegVerse Demo Suite

Runnable demonstrations of **governed AI agents, policy‑enforced execution, and receipt‑based workflow control** in the StegVerse system.

This repository provides a minimal prototype showing how autonomous agents and workflows can operate under **policy enforcement and verifiable execution receipts**.

---

# Concept

Instead of allowing systems to execute actions directly, StegVerse introduces a governed execution model:

agent intent → policy evaluation → decision → execution → receipt → next state

Each step generates a **receipt** that authorizes the next admissible operation.

---

# Demo Workflow

Demo 1 → Governance Gate  
Demo 2 → Payment / Receipt Flow  
Demo 3 → StegTalk Communication  
Demo 4 → Multi‑Agent Coordination  
Demo 5 → System Summary Document  

Each completed step produces a **receipt** that unlocks the next stage of the workflow.

---

# Running the Demo

Clone the repository:

git clone https://github.com/StegVerse-org/stegverse-demo-suite
cd stegverse-demo-suite

Run the demo:

python run_demo.py

Example output:

Running Demo 1
Receipt generated: r-demo1
Unlocked document: doc2_demo2.md

Running Demo 2
Receipt generated: r-demo2
Unlocked document: doc3_demo3.md

Running Demo 3
Receipt generated: r-demo3
Unlocked document: doc4_demo4.md

Running Demo 4
Receipt generated: r-demo4
Unlocked document: doc5_system_summary.md

---

# Repository Structure

stegverse-demo-suite/

README.md
run_demo.py

docs/
    doc1_demo1.md
    doc2_demo2.md
    doc3_demo3.md
    doc4_demo4.md
    doc5_system_summary.md

engine/
    policy_engine.py
    receipt_engine.py
    doc_gate.py

demos/
    demo1_governance_gate.py
    demo2_payment_flow.py
    demo3_stegtalk_transport.py
    demo4_multi_agent.py

receipts/
    (generated during runs)

---

# What This Demonstrates

- governed execution of agent actions
- policy‑based admission control
- receipt generation and chaining
- state‑aware workflow progression
- controlled access to information artifacts

---

# Why This Matters

StegVerse explores a model where autonomous systems operate under a **governance layer** that ensures:

- actions are authorized
- decisions are traceable
- workflows remain policy‑compliant
- execution history is verifiable

---

# Related Repositories

StegVerse SDK  
https://github.com/StegVerse-org/stegverse-sdk

---

# License

Prototype demonstration environment.
