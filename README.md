# StegVerse Demo Suite

A compact research prototype demonstrating governed execution in which
execution receipts advance system state, unlock controlled artifacts,
authorize simulated actions, and can be independently verified.

## Core pattern

- execution -> receipt -> admissible state transition -> artifact unlock
- admissible state -> action request -> action receipt -> action allowed or denied
- verification -> chain integrity -> auditable runtime evidence

## Best quick test

```bash
chmod +x stegverse
./stegverse reset
./stegverse action deploy_change
./stegverse demo
./stegverse verify
./stegverse action-receipts
```
