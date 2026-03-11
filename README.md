# StegVerse Demo Suite

A compact research prototype demonstrating governed execution in which
execution receipts advance system state, unlock controlled artifacts,
and eventually authorize simulated actions.

The suite illustrates a simple but extensible governance model:

**execution -> receipt -> admissible state transition -> artifact unlock**
**admissible state -> action request -> action receipt -> action allowed / denied**

Each workflow step produces a receipt that validates progression to the next
admissible state. Until the required execution step completes, downstream
artifacts remain inaccessible and governed actions remain denied.

## New in this version

This build adds **receipt-governed action execution**.

Preferred commands:

```bash
./stegverse reset
./stegverse explain
./stegverse action deploy_change
./stegverse demo
./stegverse action deploy_change
./stegverse action-receipts
```
