# Governed Digital Rights Mirror Handoff

## Canonical identity
- Active goal ID: `GDRC-DEMO-001`
- Active goal: Install, validate, and durably transfer the smallest public demonstration of governed digital-rights continuity for royalty-bearing media.
- Originating session goal: Demonstrate how governed AI can track ownership, authority transitions, usage, royalty allocation, and historical reconstruction for songs, albums, movies, and related digital products.
- Canonical repository: `StegVerse-org/stegverse-demo-suite`
- Default branch: `main`
- Implementation pull request: `StegVerse-org/stegverse-demo-suite#1`
- Implementation merge commit: `83ec7dc8007c00d43d202f7bc2c1a7bd17c6c612`
- Hosted-evidence branch: `chore/gdrc-hosted-validation`
- Canonical handoff: `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md`

## Current role and claims
| Task ID | State | Owner / lane | Exact surfaces | Claim release condition |
|---|---|---|---|---|
| GDRC-DEMO-001 | CLAIMED_FOR_VALIDATION | `chatgpt-session-2026-08-03-gdrc` | `demos/governed_digital_rights/task_state.json`, this handoff, hosted evidence PR | directly inspect a passing pull-request workflow job and receipt artifact, then merge the evidence handoff; otherwise classify BLOCKED with GitHub Actions as owner and a machine-observable run condition |
| GDRC-PROP-001 | MERGED_INTO_CANONICAL_WORKSTREAM | existing Site → Publisher → admissibility → Guardian chain; Master-Records only for formal custody | propagation disposition table below | no direct cross-repository mutation is authorized for the bounded fixture; a later product adoption must enter each repository through its current orchestrator and handoff |

The original implementation claim was released by merge commit `83ec7dc8007c00d43d202f7bc2c1a7bd17c6c612`. The hosted-validation claim was created at `2026-08-03T23:31:00Z` and expires at `2026-08-04T23:31:00Z` unless renewed by evidence or converted to COMPLETE/BLOCKED.

Collision boundary: no open issue, pull request, or repository search result for this capability was found before implementation. The evidence lane may change only the task-state and canonical handoff unless a hosted failure proves a bounded implementation repair is required.

## Authoritative implementation files
1. `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md`
2. `demos/governed_digital_rights/README.md`
3. `demos/governed_digital_rights/demo_case.json`
4. `demos/governed_digital_rights/task_state.json`
5. `demos/governed_digital_rights/validate_demo.py`
6. `demos/governed_digital_rights/test_validate_demo.py`
7. `schemas/governed_digital_rights_demo.schema.json`
8. `.github/workflows/governed-digital-rights-demo.yml`

`README.md` remains the repository authority boundary: this repository demonstrates receipt-bound governed scenarios and does not become an authority-bearing kernel, payment rail, legal registry, collecting society, or production intake bypass.

## Complete session execution inventory
| Task ID | Goal | Destination | Owner | State | Validation | Integration | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|
| GDRC-DEMO-001 | one song, three participants, two royalty periods | eight files above | demo-suite | implemented and merged | local PASS; hosted pending | main | PR #1; merge `83ec7dc8` | create and inspect hosted evidence PR |
| GDRC-AUTH-001 | deny unilateral label increase | fixture, evaluator, tests | demo-suite | COMPLETE | deterministic `DENY — MISSING_REQUIRED_SIGNATURES` | merged | local 9-test run | none |
| GDRC-TIME-001 | accept unanimous prospective amendment | fixture, evaluator, tests | demo-suite | COMPLETE | deterministic `ALLOW — AUTHORIZED_NON_RETROACTIVE_AMENDMENT` | merged | local 9-test run | none |
| GDRC-RECON-001 | reconstruct old and new rights states and allocations | evaluator receipt | demo-suite workflow | MACHINE_OWNED | local receipt verified; hosted artifact pending | installed | receipt hash below | inspect hosted artifact |
| GDRC-AUTO-001 | test, hash, artifact, claim-expiry visibility | GitHub Actions workflow | demo-suite / GitHub Actions | installed | hosted observation pending | main | workflow file merged | observe evidence PR run |
| GDRC-PROP-001 | classify adjacent repository obligations | this handoff and existing destination handoffs | existing canonical owners | MERGED_INTO_CANONICAL_WORKSTREAM | destination handoffs inspected | no direct mutation authorized | propagation table | none for bounded fixture |
| GDRC-STANDARD-001 | preserve expansion path to albums, films, publishing, images, games, datasets, and AI-training permissions | this handoff | future separately claimed extension | SUPERSEDED_AS_ACTIVE_TASK; requirements preserved | not activated | not part of bounded demo | design decisions below | open only through a new nonconflicting claim |

## Implemented scenario and decisions
- Initial split: artist/songwriter 50%, producer 25%, label/publisher 25%.
- Period 1: 10,000 streams and USD 100.00 distributable; USD 50.00 / 25.00 / 25.00.
- Label-only attempt to increase its share to 40%: `DENY — MISSING_REQUIRED_SIGNATURES`.
- Unanimous amendment effective after period 1: `ALLOW — AUTHORIZED_NON_RETROACTIVE_AMENDMENT`.
- New split: artist 40%, producer 35%, label 25%.
- Period 2: USD 40.00 / 35.00 / 25.00.
- Later state does not rewrite the earlier royalty period.
- Denied transitions remain visible.
- AI interpretation is not the source of rights authority; declared participants, signatures, policies, effective time, and receipts are.

## Validation evidence
Local deterministic validation performed against the committed content:

```text
unit tests: 9/9 PASS
receipt status: COMPLETE
source_case_sha256: 08f2e68f1c8b657d1630953d3a90aca6e1b0762785a48f10a995dc1350e1903e
receipt_sha256: e2172b505ec9978513d5143858b55abf0cfbd935a6adb8b852cdd6cf8d6fa784
```

Validated semantics:
- required contract and schema-document binding;
- component digest shape and unique identities;
- exact participant sets;
- 10,000-basis-point conservation;
- chronological state application;
- unanimous signature authority;
- non-retroactivity;
- deterministic largest-remainder allocation;
- royalty conservation;
- expected-decision matching;
- deterministic receipt hashing;
- stale-claim observability.

Hosted evidence is not yet claimed. The workflow was introduced by PR #1, so no pull-request-triggered run existed before it reached `main`. The branch `chore/gdrc-hosted-validation` changes the canonical task state and handoff, providing a nonproduction evidence PR that can now trigger the workflow already present on the default branch.

## Automation contract
- Owner repository: `StegVerse-org/stegverse-demo-suite`.
- Trigger: pull request, push, or manual dispatch when canonical files change.
- Inputs: fixture, schema, evaluator, tests, and persistent task state.
- Outputs: tests, deterministic JSON receipt, independent hash check, 90-day artifact.
- Fail closed on missing evidence, malformed shares, unauthorized signatures, retroactivity, expectation mismatch, allocation mismatch, or hash mismatch.
- Recognized states: COMPLETE, BLOCKED, RETRY, REVIEW_REQUIRED, FAILED, CLAIMED, SUPERSEDED, MERGED.
- Duplicate control: task ID and exact claimed paths.
- Stale claim release: `2026-08-04T23:31:00Z` unless evidence renews or closes it.

## Cross-repository propagation disposition
| Destination | Authoritative handoff inspected | Disposition for this bounded fixture | Owner and machine-observable release condition |
|---|---|---|---|
| `StegVerse-Labs/Site` | `docs/SITE_MIRROR_HANDOFF.md` | DEPENDENCY_BLOCKED / NOT DIRECTLY ADMITTED. Do not duplicate the evaluator or bypass the running Site task sequence and orchestrator. A future StegMusic/public presentation may reference the canonical demo only after Site orchestration admits a nonconflicting workload. | Site orchestrator; release when current task sequence reaches its idle terminal statement and the orchestrator admits an exact GDRC projection task. |
| `GCAT-BCAT-Engine/Publisher` | `PUBLISHER_MIRROR_HANDOFF.md` | NOT A DIRECT DESTINATION. Publisher consumes hash-bound Site activation/projection state; this demo is not Site `ACTIVATION_COMPLETE` evidence and grants no publication authority. | Existing hourly importer; release only after Site emits an explicit, hash-bound destination packet for a governed GDRC projection. |
| `StegVerse-Labs/admissibility-wiki` | `ADMISSIBILITY_WIKI_MIRROR_HANDOFF.md` | DEPENDENCY_BLOCKED. Do not create a separate interpretation before canonical Publisher evidence or an orchestrator-admitted goal. | Existing repository validation/task mesh; release after Publisher evidence exists and the wiki admits a bounded interpretation. |
| `StegVerse-002/stegguardian-wiki` | `STEGGUARDIAN_WIKI_MIRROR_HANDOFF.md` | DEPENDENCY_BLOCKED. Guardian interpretation follows bounded admissibility evidence and does not arise from demo visibility. | Guardian orchestration; release only after the upstream Site → Publisher → admissibility chain is verified. |
| `master-records/orchestration` | `ORCHESTRATION_MIRROR_HANDOFF.md` | NOT REQUIRED FOR THE COMMITTED FICTIONAL FIXTURE. Formal SDK-ingested or live usage evidence would require authenticated custody and reconstruction here. | Master-Records custody workflow; release only when a future formal/live GDRC event is submitted through an authorized intake and custody route. |

No current propagation claim remains against destination files. The unique session requirement—evaluate whether propagation is pertinent—is complete: direct propagation would violate current destination authority and sequencing. Future adoption is a new separately admitted goal, not unfinished implementation of this bounded demo.

## Durable merge records
```text
MERGED INTO: StegVerse-org/stegverse-demo-suite/main@83ec7dc8007c00d43d202f7bc2c1a7bd17c6c612
CANONICAL CONTINUATION: StegVerse-org/stegverse-demo-suite/docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md
ADJACENT ORCHESTRATION: StegVerse-Labs/Site/docs/SITE_MIRROR_HANDOFF.md
ADJACENT PUBLICATION: GCAT-BCAT-Engine/Publisher/PUBLISHER_MIRROR_HANDOFF.md
ADJACENT ADMISSIBILITY: StegVerse-Labs/admissibility-wiki/ADMISSIBILITY_WIKI_MIRROR_HANDOFF.md
ADJACENT GUARDIAN: StegVerse-002/stegguardian-wiki/STEGGUARDIAN_WIKI_MIRROR_HANDOFF.md
FORMAL/LIVE CUSTODY OWNER: master-records/orchestration/ORCHESTRATION_MIRROR_HANDOFF.md
```

## Release posture
No tag or release is authorized by this goal yet. The feature is merged, but hosted workflow and artifact inspection remain incomplete. A repository release must follow repository-wide versioning and release policy rather than treating one bounded scenario as whole-repository completion.

## Archive conditions
The session becomes archive-safe when:
1. an evidence PR triggers the installed workflow;
2. job steps and logs are inspected;
3. the uploaded receipt artifact is inspected and its hash matches the deterministic local receipt;
4. the task state is converted from CLAIMED to COMPLETE/MERGED;
5. the final evidence handoff is merged.

If GitHub Actions produces no inspectable run, the session remains temporarily retained only until the handoff records `BLOCKED`, names GitHub Actions/repository workflow enablement as owner, and gives the exact observable release condition.

## Current percentages
- Task completion: 6/7 = 86% (hosted evidence remains).
- Developed files: 8/8 = 100%; scaffolding/stubs: 0; missing: 0.
- Validation: 3/5 = 60% (static/semantic, unit, local deterministic complete; hosted job and artifact inspection pending).
- Integration: 3/4 = 75% (canonical owner, merge, propagation disposition complete; final evidence merge pending).
- Propagation assessment: 5/5 destinations classified = 100%; actual propagation correctly remains 0 because no destination admits this bounded fixture as activation evidence.
- Goal activation: 80%.
- Session consolidation: 7/7 goals durably transferred; archival blocked only by hosted validation evidence and final claim release.
