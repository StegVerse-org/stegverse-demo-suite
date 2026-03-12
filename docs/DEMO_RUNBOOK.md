# Demo Runbook

This document defines the official command sequences used to produce runtime demonstration reports.

## Report 1 — Execution Governance

```
git clone https://github.com/stegverse-org/stegverse-demo-suite
cd stegverse-demo-suite

./stegverse demo
./stegverse verify
```

Output from this sequence is captured in:

[Execution Governance Runtime Transcript](./StegVerse_Governed_Execution_Runtime_Transcript_v1.pdf)

## Report 2 — Mutation Governance

```
./stegverse reset
./stegverse runtime-info
./stegverse explain

./stegverse action deploy_change
./stegverse mutate deploy

./stegverse run demo1
./stegverse run demo2
./stegverse run demo3
./stegverse run demo4

./stegverse verify

./stegverse action deploy_change
./stegverse mutate deploy

./stegverse mutation-receipts
./stegverse reports
```