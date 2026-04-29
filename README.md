# StegVerse Demo Suite

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License](https://img.shields.io/github/license/StegVerse-org/stegverse-demo-suite)

Release: v1.0.0

The user-facing validation layer for StegVerse governance. Provides reproducible test scenarios that prove the safety stack works correctly under controlled conditions.

## Features

| Feature | Description |
|---------|-------------|
| Seed-based reproducibility | Same seed → same output |
| Reset modes | soft (warm), hard (cold), full (factory) |
| Receipt verification | SHA-256 hashed receipts with timestamp |
| GCAT/BCAT evaluation | Mathematical admissibility at commit-time |
| Deterministic output | Every run produces identical results given same seed |
| Smoke tests | Automated validation of all gates |

## Install

```bash
pip install stegverse-demo-suite
```

## Quick Start

```python
from stegverse import StegVerseSDK

sdk = StegVerseSDK()

# Run a governed demo
result = sdk.submit_intent(
    action="demo",
    mode="execution_governance",
    reset="hard"
)

print(result["status"])      # submitted
print(result["receipt_id"])  # verifiable UUID
print(result["decision"])    # allow
```

## CLI

```bash
# Run demo with reset
stegverse reset hard
stegverse demo

# Verify receipts
stegverse verify

# View reports
stegverse reports
```

## Integration

| System | Role |
|--------|------|
| StegVerse-SDK | Core governance primitives |
| demo_ingest_engine | Orchestrated bundle ingestion |
| StegDB | Execution state monitoring |
| AaCT-E | Audit trail archival |

## Links

- Repository: https://github.com/StegVerse-org/stegverse-demo-suite
- Issues: https://github.com/StegVerse-org/stegverse-demo-suite/issues

---

**StegVerse: Execution is not assumed. Execution is admitted.**
