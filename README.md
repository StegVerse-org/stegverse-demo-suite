# StegVerse Demo Suite

A compact research prototype demonstrating governed execution in which
execution receipts advance system state, unlock controlled artifacts,
and eventually authorize simulated actions.

The suite illustrates a simple but extensible governance model:

- execution -> receipt -> admissible state transition -> artifact unlock
- admissible state -> action request -> action receipt -> action allowed or denied

This version adds **receipt-governed action execution**.

## Quick test

```bash
chmod +x stegverse
./stegverse reset
./stegverse action deploy_change
./stegverse demo
./stegverse action deploy_change
./stegverse action-receipts
```
