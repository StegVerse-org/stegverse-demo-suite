# Demo Evaluator Mirror Handoff

## Active goal and goal ID

goal_id: DEMO-EVALUATOR-PORTABLE-001
originating_session_goal: Provide Mansoor a portable StegVerse evaluation package without requiring paid hosted runtime, GitHub Actions, Render, or access to sovereign control-plane repositories.
repository: StegVerse-org/stegverse-demo-suite
branch: feat/mansoor-evaluator-package-20260811
canonical_task_owner: StegVerse-org/stegverse-demo-suite
active_implementation_claim: CLAIMED_FOR_IMPLEMENTATION
active_validation_claim: CLAIMED_FOR_VALIDATION
claim_created: 2026-08-11
claim_release_condition: evaluator profile, local package builder, deterministic verifier, and README boundary are merged and validated; resulting package is reproducible without hosted compute.

## Authority boundary

This repository is a public demonstration and evaluator-distribution surface. It is not an authority-bearing kernel and grants no execution, governance, wallet, signing, broadcast, custody, provider-credential, heartbeat, or production activation authority.

Evaluator connectivity is deliberately narrower than the rest of StegVerse:

- permitted StegVerse execution/sandbox connection: `StegGhost/entity-sandbox-runner` only;
- `StegVerse-org/LLM-adapter`: EXCLUDED from the evaluator package and evaluator runtime boundary;
- active StegVerse-Labs control-plane repositories: EXCLUDED unless an immutable public artifact is explicitly copied into the evaluator bundle;
- provider credentials, API keys, wallet secrets, TV/TVC capability material, private receipts, and live runtime state: PROHIBITED;
- GitHub Actions and Render: not required to build, verify, inspect, or run the evaluator package.

GitHub may remain a convenient public storage/discovery surface. Its availability is not a prerequisite for a previously built portable bundle to remain usable.

## Evaluator experience

The package has two layers:

1. `mansoor-evaluation`: a fixed, versioned, self-contained evaluation package containing the selected product snapshot, architecture/readme, validation instructions, deterministic tests, schemas, example receipts, performance/benchmark material when included, and an exact manifest of all files.
2. `demo-suite-explorer`: optional read-only exploration of other public demo-suite products and scenarios. Exploring those demos does not widen the evaluator package authority or expose excluded repositories.

The evaluator may inspect, execute deterministic local demos, and route adversarial/entity-specific demo fixtures to StegGhost where separately available. The evaluator may not acquire access to LLM-adapter, production heartbeat state, active trading credentials, vault material, wallets, TV/TVC capability material, or private StegVerse repositories through this package.

## Authoritative files

- `config/evaluator_profile.json`
- `scripts/build_evaluator_bundle.py`
- `scripts/verify_evaluator_bundle.py`
- `docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md`
- `README.md`

## Machine-owned tasks

- bundle creation: `scripts/build_evaluator_bundle.py`
- bundle verification: `scripts/verify_evaluator_bundle.py`
- output manifest: `EVALUATOR_MANIFEST.json`

## Validation commands

```bash
python scripts/build_evaluator_bundle.py --output dist/mansoor-evaluation
python scripts/verify_evaluator_bundle.py dist/mansoor-evaluation
```

The builder and verifier must run with the Python standard library only and without network access.

## Cross-repository dependencies

Required runtime dependency: NONE.
Optional evaluator sandbox accessibility: `StegGhost/entity-sandbox-runner`.
Explicitly excluded: `StegVerse-org/LLM-adapter`.

The package may include immutable copied artifacts from other repositories only when their exact source repository, commit, path, and SHA-256 are recorded in the manifest. A copied artifact grants no live repository access.

## Incomplete work

- install evaluator profile;
- install local deterministic bundle builder;
- install local deterministic verifier;
- update README evaluator boundary;
- validate package reproducibility and exclusion rules;
- merge and release claim.

## Propagation obligations

This evaluator surface does not replace canonical product repositories. It provides a bounded review package and public demo discovery surface. Any evaluator findings that affect production must be carried back through the canonical repository and governance path.

## Archive conditions

This scoped task is complete when the evaluator package can be created and verified locally with no third-party runtime dependency, LLM-adapter is excluded, StegGhost is the only permitted external StegVerse sandbox connection, and all claims/evidence are durably recorded.

Developed-files percentage: 20%
Validation percentage: 0%
Integration percentage: 20%
Goal-activation percentage: 20%
Session-consolidation state: ACTIVE — UNIQUE WORK REMAINS
