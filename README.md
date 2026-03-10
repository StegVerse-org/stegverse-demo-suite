# StegVerse Demo Suite

Runnable demonstrations of a **governed distributed operating system for AI agents**.

StegVerse introduces a runtime where autonomous agents, services, and workflows execute through **policy enforcement and verifiable execution receipts**.

---

## Quick Start

Clone the repository and run the full governed workflow:

```bash
python run_demo.py
```

The entire demo runs locally and requires no external services.

This will execute a sequence of governed steps:

```
Demo 1 → Governance Gate
Demo 2 → Payment / Receipt Flow
Demo 3 → StegTalk Communication
Demo 4 → Multi-Agent Coordination
Demo 5 → System Summary
```

Each step produces a **receipt** that authorizes the next admissible operation.

---

## Architecture

```
Agent / Human / Service
        │
        ▼
      Intent
        │
        ▼
  StegVerse Admission Layer
   (policy + governance)
        │
   allow | deny | defer
        │
        ▼
      Execution
        │
        ▼
       Receipt
        │
        ▼
 Next Admissible State
 (document / action)
```

---

## What This Demonstrates

The demo illustrates several core StegVerse primitives:

• governed execution of agent actions  
• policy-based admission control  
• receipt-based workflow progression  
• dependency-aware multi-agent coordination  
• controlled access to information artifacts  

---

## Why This Matters

Autonomous AI systems increasingly interact with real infrastructure.

StegVerse explores a model where those systems operate under a **governance runtime** that ensures:

• actions are authorized before execution  
• workflows remain policy-compliant  
• execution history is verifiable  
• multi-agent coordination remains controlled  

---

## Running Individual Components

You can run demos individually:

```bash
python stegverse_cli.py run demo1
python stegverse_cli.py run demo2
python stegverse_cli.py run demo3
python stegverse_cli.py run demo4
```

Check system state:

```bash
python stegverse_cli.py status
python stegverse_cli.py receipts
```

Retrieve governed documents:

```bash
python stegverse_cli.py retrieve doc1
python stegverse_cli.py retrieve doc2
python stegverse_cli.py retrieve doc3
python stegverse_cli.py retrieve doc4
python stegverse_cli.py retrieve doc5
```

---

## Related Repositories

StegVerse SDK  
https://github.com/StegVerse-org/stegverse-sdk

---

## License

Prototype demonstration environment.
