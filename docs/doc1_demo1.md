# Demo 1 — Governance Gate

## Purpose

This first demo shows the simplest StegVerse primitive:

**an action is proposed, evaluated by policy, and either admitted or blocked before execution.**

This is the foundation of the StegVerse runtime model.

---

## What This Demo Proves

- actions do not execute directly
- a policy gate evaluates admissibility first
- a receipt is generated to record the governed transition
- successful completion unlocks the next workflow artifact

---

## Expected Flow

```text
agent intent
→ policy evaluation
→ allow / deny / defer
→ receipt
→ next state
```

---

## Example Outcome

A deployment request may be:

- **allowed** if constraints are satisfied
- **deferred** if quorum is required
- **denied** if policy forbids execution

---

## What To Run

Use the CLI:

```bash
python stegverse_cli.py run demo1
```

Or use the demo runner directly if present:

```bash
python run_demo.py
```

---

## Success Condition

The demo succeeds when:

- a receipt is generated for Demo 1
- the receipt is recorded in the local receipt chain
- **Doc 2** becomes retrievable

---

## Next Step

Retrieve the next governed artifact:

```bash
python stegverse_cli.py retrieve doc2
```

If access is valid and the timer has not expired, the system will return **Doc 2**.
