# Demo Evaluator Mirror Handoff

## Active goal and goal ID

goal_id: DEMO-EVALUATOR-PORTABLE-001
originating_session_goal: Provide a general, identity-neutral, portable StegVerse evaluation/development surface that remains usable without paid hosted runtime, GitHub Actions, Render, or access to sovereign control-plane repositories.
repository: StegVerse-org/stegverse-demo-suite
branch: feat/general-sdk-evaluator-surface-20260812
canonical_task_owner: StegVerse-org/stegverse-demo-suite
active_implementation_claim: CLAIMED_FOR_IMPLEMENTATION
active_validation_claim: CLAIMED_FOR_VALIDATION
claim_created: 2026-08-12
claim_release_condition: identity-neutral frozen bundle, SDK capability catalog, per-component licensing provenance, local builder/verifier, terms/relationship integration, and bounded SDK-mediated StegGhost/LLM-adapter routes are validated and merged.

## Supersession

The earlier branch `feat/mansoor-evaluator-package-20260811` is SUPERSEDED as an implementation source. No recipient-specific package or directory is canonical. Mansoor and any later evaluator/developer use the same general SDK-governed relationship surface.

## Authority boundary

This repository is a public demonstration and evaluator/developer distribution surface. It is not an authority-bearing kernel and grants no execution, governance, wallet, signing, broadcast, custody, provider-credential, heartbeat, production activation, private-repository, or sovereign-runtime authority.

The portable bundle itself has no direct StegVerse service connection. Interactive access is mediated by `StegVerse-org/StegVerse-SDK` after affirmative acceptance of the Demo TOS/TOU and creation of a bounded evaluation relationship.

Permitted SDK-mediated routes when specifically admitted by that relationship:

- `StegGhost/entity-sandbox-runner` evaluator sandbox;
- `StegVerse-org/LLM-adapter:evaluator-entry` restricted evaluator facade.

Direct LLM-adapter access is prohibited. Provider credentials, API keys, wallet secrets, TV/TVC capability material, private receipts, private repositories, and live sovereign runtime state are prohibited from the portable bundle.

GitHub Actions and Render are not required to build, verify, inspect, or run the frozen local package. Third-party accessibility is fallback; StegVerse continuity and local package usability remain primary.

## Evaluator/developer experience

```text
frozen portable package
-> local inspection / deterministic demos / local verification
-> Demo TOS + TOU affirmative acceptance before connection
-> SDK evaluator states objectives and optional restrictions
-> SDK resolves admitted / denied / unresolved capability sets
-> optional SDK-mediated StegGhost or LLM-adapter evaluator route
-> bounded receipts
```

The evaluator may narrow their own relationship. A request to broaden it is re-evaluated by the SDK and does not create authority by request alone.

## Frozen-state model

The package is identity-neutral and represents a declared immutable source revision. Optional `frozen_payload/` content contains copied immutable artifacts only. `EVALUATOR_MANIFEST.json` hashes every included file and records the represented source revision.

A frozen package is evidence of that frozen state only and is not current-production-state evidence.

## Licensing

`config/evaluator_license_manifest.json` identifies the applicable component license, source repository/ref, license path, Git blob identity, and SHA-256 for evaluator-facing components.

Software-license rights and Demo service/SDK relationship access are separate boundaries. The Demo TOS/TOU do not silently revoke rights independently granted by an applicable component license, and an open-source license does not grant live StegVerse service, credential, private-repository, or sovereign authority.

## Authoritative files

- `config/evaluator_profile.json`
- `config/evaluator_capability_catalog.json`
- `config/evaluator_license_manifest.json`
- `scripts/build_evaluator_bundle.py`
- `scripts/verify_evaluator_bundle.py`
- `tests/test_evaluator_bundle.py`
- `docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md`
- `README.md`

Cross-repository authorities:

- Demo terms and evaluator relationship: `StegVerse-org/StegVerse-SDK/SDK_MIRROR_HANDOFF.md` + `docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md`;
- restricted LLM evaluator facade: `StegVerse-org/LLM-adapter` scoped evaluator-entry handoff;
- optional sandbox implementation: `StegGhost/entity-sandbox-runner`.

## Machine-owned tasks

- bundle creation: `scripts/build_evaluator_bundle.py`;
- bundle verification: `scripts/verify_evaluator_bundle.py`;
- output manifest: `EVALUATOR_MANIFEST.json`;
- capability catalog: `config/evaluator_capability_catalog.json`;
- license manifest: `config/evaluator_license_manifest.json`.

## Validation commands

```bash
python -m unittest tests.test_evaluator_bundle
python scripts/build_evaluator_bundle.py --output dist/evaluation --source-revision <immutable-source-revision>
python scripts/verify_evaluator_bundle.py dist/evaluation
```

The builder and verifier use the Python standard library only and require no network access.

## Cross-repository dependencies

Required runtime dependency for the frozen package: NONE.
Required relationship manager for interactive connections: `StegVerse-org/StegVerse-SDK`.
Optional SDK-mediated sandbox capability: `StegGhost/entity-sandbox-runner`.
Optional SDK-mediated model capability: `StegVerse-org/LLM-adapter:evaluator-entry`.

A copied artifact grants no live repository access.

## Incomplete work

- merge and validate Demo TOS/TOU acceptance gate in StegVerse-SDK;
- finish evaluator-scoped LLM-adapter entry contract and tests;
- update final frozen license/source refs after those merges;
- perform deterministic local bundle build + verification from the generalized branch;
- merge generalized Demo surface and release claims.

## Propagation obligations

The Demo surface does not replace canonical product repositories. Evaluator findings affecting production return through the owning repository and governance path. Commercial agreements and exclusivity are separate from technical availability unless a separately executed agreement expressly requires a technical restriction.

## Archive conditions

This scoped task is complete when the identity-neutral frozen package can be created and verified locally, licensing is complete, Demo TOS/TOU acceptance is required before SDK connection, LLM-adapter/StegGhost are reachable only through admitted SDK relationships, no recipient-specific package remains canonical, and all claims/evidence are durably recorded.

Developed-files percentage: 80%
Validation percentage: 50%
Integration percentage: 65%
Goal-activation percentage: 60%
Session-consolidation state: ACTIVE — UNIQUE WORK REMAINS
