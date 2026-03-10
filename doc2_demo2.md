# Demo 2 — Payment and Receipt Flow

## Purpose

This demo shows how StegVerse receipts can govern a simple financial-style workflow.

The point is not full banking functionality.  
The point is to demonstrate that **state transitions involving value can be made verifiable and sequential**.

---

## What This Demo Proves

- payment-like actions can be governed
- receipts can authorize the next workflow transition
- value transfer can be represented as receipt-backed progression

---

## Expected Flow

```text
payment intent
→ policy evaluation
→ execution decision
→ receipt
→ next governed document unlock
```

---

## What To Run

```bash
python stegverse_cli.py run demo2
```

---

## Success Condition

The demo succeeds when:

- a payment-flow receipt is generated
- the receipt is chained after Demo 1
- **Doc 3** becomes retrievable within the allowed time window

---

## Next Step

Try to retrieve the next document:

```bash
python stegverse_cli.py retrieve doc3
```

Or test bulk retrieval:

```bash
python stegverse_cli.py retrieve-all
```

You should see that some artifacts remain blocked until their workflow conditions are satisfied.