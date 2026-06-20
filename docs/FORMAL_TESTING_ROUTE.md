# Formal Testing Route Reference

This repository is the public demo validation route.

It should consume formal testing datasets only after `StegVerse-org/StegVerse-SDK` has bound the dataset to a manifest and intake receipt.

## Required Flow

```text
Dataset / fixture / governance artifact
→ StegVerse-org/StegVerse-SDK ingestion
→ manifest binding
→ receipt binding
→ public demo validation route
→ deterministic demo result receipt
```

## Route Responsibility

The demo-suite demonstrates reproducible, public, explainable validation behavior.

It should not replace:

- `StegGhost/entity-sandbox-runner` for adversarial or entity sandbox testing;
- `StegVerse-Labs/Standing-Proof-Engine` for commit-time standing proof;
- `StegVerse-Labs/Boundary-Test` for GLM-style boundary declaration and manifest composability cases.

## Receipt Rule

Every demo result must preserve the SDK intake manifest reference and SDK intake receipt reference.
