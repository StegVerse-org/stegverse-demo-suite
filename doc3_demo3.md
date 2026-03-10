# Demo 3 — StegTalk Communication

## Purpose

This demo shows how StegVerse primitives support a communication workflow.

The message path is simplified for demonstration, but the key architectural idea is preserved:

**communication can be treated as a governed state transition with a receipt.**

---

## What This Demo Proves

- messaging events can be receipt-backed
- communication steps can be integrated into governed workflows
- information movement can be recorded as a valid state transition

---

## Expected Flow

```text
message intent
→ policy evaluation
→ admitted communication action
→ receipt
→ next workflow artifact unlocked
```

---

## What To Run

```bash
python stegverse_cli.py run demo3
```

---

## Success Condition

The demo succeeds when:

- a communication receipt is generated
- the receipt chain now includes messaging
- **Doc 4** becomes retrievable if the time window is still valid

---

## Next Step

Retrieve the next governed artifact:

```bash
python stegverse_cli.py retrieve doc4
```

If the unlock window expired, rerun the prior step and try again.