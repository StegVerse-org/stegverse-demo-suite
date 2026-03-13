# StegVerse Demo Suite

![Release](https://img.shields.io/github/v/release/StegVerse-org/stegverse-demo-suite)
![CI](https://img.shields.io/github/actions/workflow/status/StegVerse-org/demo-suite-runner/run-demo.yml)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/github/license/StegVerse-org/stegverse-demo-suite)

A compact research prototype demonstrating governed execution in which
execution receipts advance system state, unlock controlled artifacts,
authorize simulated actions, govern mutations, and can be independently verified.

## Best quick test

```bash
chmod +x stegverse
./stegverse reset
./stegverse runtime-info
./stegverse action deploy_change
./stegverse mutate deploy
./stegverse demo
./stegverse verify
./stegverse reports
./stegverse mutation-receipts
```
