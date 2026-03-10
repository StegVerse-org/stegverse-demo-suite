# Demo 4 — Multi-Agent Governance

## Purpose

This demo shows the most important escalation in the StegVerse demo suite:

**multiple agents coordinate through governed receipts and dependency-aware execution.**

This is where StegVerse begins to resemble a real control plane.

---

## What This Demo Proves

- multiple agents can participate in the same workflow
- execution can require quorum or dependency satisfaction
- receipts can encode causality across agents
- governed workflows are not limited to single actions

---

## Expected Flow

Example pattern:

```text
Planner → proposes
Executor → attempts action
Finance → approves
Guardian → approves
Executor → retries
Action admitted
```

Each step produces a receipt.

---

## What To Run

```bash
python stegverse_cli.py run demo4
```

---

## Success Condition

The demo succeeds when:

- multiple receipts are generated
- dependencies are visible
- the workflow reaches completion
- **Doc 5** becomes permanently accessible

---

## Next Step

Retrieve the final system summary:

```bash
python stegverse_cli.py retrieve doc5
```

This final document summarizes the whole governed workflow.
