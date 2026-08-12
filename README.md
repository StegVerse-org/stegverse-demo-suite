# StegVerse Demo Suite

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)

Release: v1.0.0

`stegverse-demo-suite` is the public, reproducible demonstration layer for StegVerse governance scenarios. It demonstrates controlled, explainable test cases after data has already been ingested through the SDK and bound to a manifest and receipt. It is not an authority-bearing kernel and does not bypass SDK intake.

## General portable evaluator/developer surface

This repository owns an identity-neutral, frozen evaluator/distribution profile for anyone who wants to evaluate, inspect, develop against, or prepare a proposal for StegVerse without requiring GitHub Actions, Render, or a hosted StegVerse runtime.

```text
frozen portable bundle
-> local inspection / deterministic verification
-> Demo TOS + TOU affirmative acceptance
-> StegVerse SDK evaluation relationship
-> evaluator states what they care to evaluate
-> SDK admits only the intersection of requested scope + package catalog + StegVerse policy
-> optional SDK-mediated StegGhost sandbox
-> optional SDK-mediated LLM-adapter evaluator entry
```

The portable bundle itself has no direct StegVerse service connection. Direct access to `StegGhost/entity-sandbox-runner` or `StegVerse-org/LLM-adapter` is not granted by possessing the bundle. Both interactive routes require an admitted SDK relationship; direct LLM-adapter access is prohibited. The package grants no production activation, heartbeat, governance, wallet signing, transaction broadcast, custody, provider-credential, TV/TVC capability-material, private-repository, or sovereign-runtime authority.

Build and verify locally with only the Python standard library:

```bash
python scripts/build_evaluator_bundle.py --output dist/evaluation --source-revision <immutable-source-revision>
python scripts/verify_evaluator_bundle.py dist/evaluation
```

An optional local `frozen_payload/` directory may contain immutable copied evaluation artifacts from another StegVerse product. The resulting `EVALUATOR_MANIFEST.json` hashes every bundled file and records the represented source revision. A copied artifact does not grant access to its source repository or runtime.

The evaluator capability catalog is `config/evaluator_capability_catalog.json`. Per-component software licensing and provenance are declared in `config/evaluator_license_manifest.json`. Software-license rights and Demo service/SDK relationship access are separate boundaries. See `docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md` and `config/evaluator_profile.json`.

## Formal testing route

```text
Dataset / fixture / governance artifact
-> StegVerse-org/StegVerse-SDK ingestion
-> manifest binding
-> receipt binding
-> public demo validation route
-> deterministic demo result receipt
```

Route role: SDK ingests. Demo-suite demonstrates. Receipts bind every transition. More adversarial, entity-specific, or standing-specific cases should be routed through the applicable admitted SDK relationship or the owning production repository after SDK intake.

## Features

| Feature | Description |
|---|---|
| Seed-based reproducibility | Same seed produces the same output. |
| Reset modes | soft, hard, and full reset demonstrations. |
| Receipt verification | SHA-256 receipt and timestamp demonstrations. |
| GCAT/BCAT evaluation | Demonstrates admissibility checks at controlled commit points. |
| Deterministic output | Repeatable results for public inspection. |
| Smoke tests | Automated validation of demonstration paths. |
| Portable evaluator bundle | Identity-neutral frozen packaging and local verification without hosted runtime dependencies. |

## Install

```bash
pip install stegverse-demo-suite
```

## Quick start

```python
from stegverse import StegVerseSDK

sdk = StegVerseSDK()
result = sdk.submit_intent(action="demo", mode="execution_governance", reset="hard")
print(result["status"])
print(result["receipt_id"])
print(result["decision"])
```

## Integration

| System | Role |
|---|---|
| `StegVerse-org/StegVerse-SDK` | Governs evaluator relationship intake and manifest-bound, receipt-bound demo datasets. |
| `StegVerse-org/demo_ingest_engine` | Org-side orchestration and result-return boundary. |
| `StegVerse-org/demo-suite-runner` | Formal runner route for GCAT/BCAT probes. |
| `StegGhost/entity-sandbox-runner` | Optional evaluator sandbox capability, reachable only through an admitted SDK relationship. |
| `StegVerse-org/LLM-adapter` | Optional evaluator LLM capability, reachable only through the restricted SDK evaluator entry; direct adapter access is not part of the Demo surface. |
| `StegVerse-Labs/Standing-Proof-Engine` | Standing proof route outside the evaluator package. |
| `StegVerse-Labs/Boundary-Test` | Boundary / GLM case route outside the evaluator package. |

## Boundary rule

Public demonstration does not imply general deployment authority, external endorsement, compatibility recognition, provenance recognition, collaboration, or validation by a reviewer. The portable evaluator profile is a distribution boundary, not a privilege bridge. Access to the package or public demo suite does not imply access to private repositories, production services, active governance state, credentials, wallets, TV/TVC capability material, the full LLM-adapter surface, or sovereign runtime control.

## Links

- Repository: https://github.com/StegVerse-org/stegverse-demo-suite
- Issues: https://github.com/StegVerse-org/stegverse-demo-suite/issues
