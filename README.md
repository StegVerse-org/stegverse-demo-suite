# StegVerse Demo Suite

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

Release: v1.0.0

`stegverse-demo-suite` is the public, reproducible demonstration layer for StegVerse governance scenarios.

It demonstrates controlled, explainable test cases after data has already been ingested through the SDK and bound to a manifest and receipt. It is not an authority-bearing kernel and does not bypass SDK intake.

---

## Portable evaluator profile

This repository also owns a bounded evaluator-distribution profile for sharing a self-contained product evaluation package without requiring GitHub Actions, Render, or any hosted StegVerse runtime.

The evaluator boundary is intentionally narrow:

```text
portable evaluator package
→ deterministic local inspection and tests
→ optional read-only demo-suite exploration
→ optional StegGhost/entity-sandbox-runner for adversarial/entity-specific demo cases
```

`StegVerse-org/LLM-adapter` is explicitly excluded from the evaluator package and evaluator runtime boundary. The package grants no production activation, heartbeat, governance, wallet signing, transaction broadcast, custody, provider-credential, TV/TVC capability-material, or private-repository authority.

Build and verify locally with only the Python standard library:

```bash
python scripts/build_evaluator_bundle.py --output dist/mansoor-evaluation
python scripts/verify_evaluator_bundle.py dist/mansoor-evaluation
```

An optional local `evaluation_payload/` directory may contain immutable copied evaluation artifacts from another StegVerse product. The resulting `EVALUATOR_MANIFEST.json` hashes every bundled file. A copied artifact does not grant access to its source repository or runtime.

See `docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md` and `config/evaluator_profile.json`.

---

## Formal testing route

This repository consumes formal testing datasets only after they have been ingested through `StegVerse-org/StegVerse-SDK` and bound to a manifest and intake receipt.

```text
Dataset / fixture / governance artifact
→ StegVerse-org/StegVerse-SDK ingestion
→ manifest binding
→ receipt binding
→ public demo validation route
→ deterministic demo result receipt
```

Route role:

```text
SDK ingests.
Demo-suite demonstrates.
Receipts bind every transition.
```

More adversarial, entity-specific, or standing-specific cases should be routed to `StegGhost/entity-sandbox-runner` or `StegVerse-Labs/Standing-Proof-Engine` after SDK intake.

---

## Features

| Feature | Description |
|---|---|
| Seed-based reproducibility | Same seed produces the same output. |
| Reset modes | soft, hard, and full reset demonstrations. |
| Receipt verification | SHA-256 receipt and timestamp demonstrations. |
| GCAT/BCAT evaluation | Demonstrates admissibility checks at controlled commit points. |
| Deterministic output | Repeatable results for public inspection. |
| Smoke tests | Automated validation of demonstration paths. |
| Portable evaluator bundle | Local deterministic packaging and verification without hosted runtime dependencies. |

---

## Install

```bash
pip install stegverse-demo-suite
```

---

## Quick start

```python
from stegverse import StegVerseSDK

sdk = StegVerseSDK()

result = sdk.submit_intent(
    action="demo",
    mode="execution_governance",
    reset="hard",
)

print(result["status"])
print(result["receipt_id"])
print(result["decision"])
```

---

## Integration

| System | Role |
|---|---|
| `StegVerse-org/StegVerse-SDK` | Governed ingestion point for manifest-bound, receipt-bound demo datasets. |
| `StegVerse-org/demo_ingest_engine` | Org-side orchestration and result-return boundary. |
| `StegVerse-org/demo-suite-runner` | Formal runner route for GCAT/BCAT probes. |
| `StegGhost/entity-sandbox-runner` | Rigorous sandbox route for adversarial/entity tests and the only permitted external StegVerse execution surface for the portable evaluator profile. |
| `StegVerse-Labs/Standing-Proof-Engine` | Standing proof route for stale-state and authority-rebinding cases outside the evaluator package. |
| `StegVerse-Labs/Boundary-Test` | Boundary / GLM case route for neutral declaration and composability fixtures outside the evaluator package. |
| `StegVerse-org/LLM-adapter` | Explicitly excluded from the portable evaluator profile. |

---

## Boundary rule

Public demonstration does not imply general deployment authority, external endorsement, compatibility recognition, provenance recognition, collaboration, or validation by a reviewer. Demonstrations are bounded, receipt-oriented, and reproducible.

The portable evaluator profile is a distribution boundary, not a privilege bridge. Access to the package or public demo suite does not imply access to private repositories, production services, active governance state, credentials, wallets, TV/TVC capability material, LLM-adapter, or sovereign runtime control.

---

## Links

- Repository: https://github.com/StegVerse-org/stegverse-demo-suite
- Issues: https://github.com/StegVerse-org/stegverse-demo-suite/issues
