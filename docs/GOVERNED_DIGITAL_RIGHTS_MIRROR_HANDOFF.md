# Governed Digital Rights Mirror Handoff

## Canonical identity
- Active goal ID: `GDRC-DEMO-001`
- Active goal: Install and validate the smallest public demonstration of governed digital-rights continuity for royalty-bearing media.
- Originating session goal: Demonstrate how governed AI can track ownership, authority transitions, usage, royalty allocation, and historical reconstruction for songs, albums, movies, and related digital products.
- Repository: `StegVerse-org/stegverse-demo-suite`
- Branch: `feat/governed-digital-rights-demo`
- Canonical handoff: `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md`
- Canonical task owner: `StegVerse-org/stegverse-demo-suite`

## Active claims
| Task ID | Claim state | Role | Claimant | Exact surfaces | Created | Expiration / release condition | Expected evidence |
|---|---|---|---|---|---|---|---|
| GDRC-DEMO-001 | CLAIMED_FOR_IMPLEMENTATION | implementation + local validation | `chatgpt-session-2026-08-03-gdrc` | `demos/governed_digital_rights/**`, `schemas/governed_digital_rights_demo.schema.json`, `.github/workflows/governed-digital-rights-demo.yml`, this handoff | 2026-08-03T18:19:00-05:00 | Release on merged PR, explicit transfer, or 2026-08-04T18:19:00-05:00 if no evidence-bearing commit appears | committed files, deterministic test receipt, workflow result |
| GDRC-PROP-001 | CLAIMED_FOR_INTEGRATION | propagation assessment only | `chatgpt-session-2026-08-03-gdrc` | Site, Publisher, admissibility-wiki, stegguardian-wiki contracts/handoffs | 2026-08-03T18:19:00-05:00 | Release after canonical demo PR records exact propagation decision | committed propagation decision or durable blocked task |

Collision boundary: no other branch, issue, pull request, workflow, or machine task containing `royalty`, `rights`, `ownership`, `song`, or `digital` was found open in this repository before claim creation. This claim does not authorize changes to SDK intake, kernel authority, payout execution, external collecting-society systems, or production payment rails.

## Authoritative files
- `README.md` — repository boundary: public reproducible demonstrations after SDK ingestion and receipt binding.
- `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md` — canonical continuation and claim record for this goal.
- `demos/governed_digital_rights/README.md` — scenario contract and operator instructions.
- `demos/governed_digital_rights/demo_case.json` — canonical asset, rights, usage, transition, and expected-decision fixture.
- `demos/governed_digital_rights/validate_demo.py` — deterministic evaluator and receipt generator.
- `demos/governed_digital_rights/test_validate_demo.py` — conformance tests.
- `schemas/governed_digital_rights_demo.schema.json` — input contract.
- `.github/workflows/governed-digital-rights-demo.yml` — repository-native validation and receipt artifact path.

## Session goal inventory
| Task ID | Goal | Destination | State | Validation | Integration | Archival dependency | Next executable action |
|---|---|---|---|---|---|---|---|
| GDRC-DEMO-001 | Single-song, three-party, one-usage-period demo | this repository and branch | CLAIMED_FOR_IMPLEMENTATION | pending | canonical owner selected | yes | install fixture, validator, tests, workflow |
| GDRC-AUTH-001 | Deny unauthorized split mutation | `demos/governed_digital_rights/validate_demo.py` and fixture | CLAIMED_FOR_IMPLEMENTATION | pending | same demo | yes | assert deterministic `DENY` |
| GDRC-TIME-001 | Accept authorized future-effective amendment without rewriting prior royalty period | validator and fixture | CLAIMED_FOR_IMPLEMENTATION | pending | same demo | yes | assert old/new split by effective time |
| GDRC-RECON-001 | Independently reconstruct rights and allocations for both periods | generated receipt/report | CLAIMED_FOR_IMPLEMENTATION | pending | same demo | yes | emit canonical SHA-256 receipt |
| GDRC-AUTO-001 | Automate validation, stale-claim visibility, and receipt artifact creation | GitHub Actions workflow | CLAIMED_FOR_IMPLEMENTATION | pending | repository-native | yes | install workflow |
| GDRC-PROP-001 | Determine propagation obligation to Site, Publisher, admissibility-wiki, stegguardian-wiki, and master-records | this handoff plus destination-specific durable task if required | CLAIMED_FOR_INTEGRATION | pending | not yet propagated | yes | inspect applicable destination handoffs after canonical demo evidence exists |
| GDRC-STANDARD-001 | Preserve broader standardization path for albums, movies, publishing, images, games, datasets, and AI-training permissions | this handoff | MERGED_INTO_CANONICAL_WORKSTREAM | design preserved, not implemented | future extensions must remain bounded to demo evidence | no after this handoff commits | retain as non-activated roadmap, not a completion claim |

## Design decisions transferred from the originating session
1. The smallest presentation is one fictional song, three rights participants, one reported usage period, one unauthorized ownership mutation, and one properly authorized future-effective amendment.
2. Rights state is not a single owner field. The demo separately records asset identity, participants, shares, authority, effective time, usage, calculation policy, allocation, attempted mutation, accepted amendment, and reconstruction evidence.
3. AI may interpret and reconcile records, but signed authority declarations, policy references, and receipts remain the source of truth.
4. Historical state is immutable: a later amendment must not retroactively change an earlier allocation.
5. Invalid transitions remain visible as denied events rather than disappearing.
6. The public demo proves deterministic governed evaluation only. It does not assert legal title, external platform integration, collection-society recognition, payment settlement, or production authority.
7. The presentation question is: `Who gets paid—and can the answer be proven?`

## Planned deterministic scenario
- Asset: one fictional master recording and composition.
- Initial split: artist/songwriter 50%, producer 25%, label/publisher 25%.
- Usage period 1: 10,000 streams, distributable royalty USD 100.00.
- Expected allocation 1: USD 50.00 / 25.00 / 25.00.
- Unauthorized attempt: label attempts to increase its share from 25% to 40% without the required unanimous participant signatures; expected `DENY`.
- Authorized amendment: artist transfers 10 percentage points to producer with all required signatures, effective after period 1.
- New split: artist 40%, producer 35%, label 25%.
- Usage period 2: same distributable royalty for clear comparison; expected USD 40.00 / 35.00 / 25.00.

## Automation contract
Trigger: pull request and push changes affecting the canonical files, plus manual dispatch.
Inputs: committed fixture, schema, evaluator, and tests.
Outputs: test status and generated JSON receipt artifact.
Persistent state: Git history, this handoff, workflow run, and uploaded receipt artifact.
Fail-closed rules: missing required evidence, invalid shares, unsigned amendment, retroactive amendment, mismatched expected result, or hash mismatch must fail validation.
States represented: COMPLETE, BLOCKED, RETRY, REVIEW_REQUIRED, FAILED, CLAIMED, SUPERSEDED, MERGED.
Duplicate prevention: the task ID and exact path claim in this handoff define the collision boundary; stale claim expiration is machine-checked by the validator workflow.

## Completion and archive conditions
This originating session may be archived only after:
1. all planned canonical files are committed;
2. local deterministic tests pass;
3. a pull request exists and its workflow jobs/logs are inspected;
4. the workflow receipt artifact is inspected or its absence is durably recorded with a named blocked owner and release condition;
5. the claim is released or transferred;
6. propagation obligations are either completed or installed as exact durable tasks in the appropriate destination handoffs/issues;
7. this handoff contains final evidence references and percentages.

## Current state
- Completed work: canonical owner selected; convergence search completed; branch and implementation claim created; session-specific design decisions transferred.
- Incomplete work: fixture, schema, evaluator, tests, workflow, receipt, PR, workflow inspection, propagation assessment, claim release.
- Blockers: none at handoff creation.
- Machine-owned tasks: none active until workflow installation.
- Cross-repository dependencies: SDK ingestion and receipt binding are architectural prerequisites for production/formal intake, but this repository may validate a bounded committed fixture without claiming intake activation.

## Validation commands
```bash
python demos/governed_digital_rights/validate_demo.py \
  --input demos/governed_digital_rights/demo_case.json \
  --schema schemas/governed_digital_rights_demo.schema.json \
  --output build/governed-digital-rights/receipt.json
python -m unittest demos.governed_digital_rights.test_validate_demo -v
```

## Percentages at handoff creation
- Developed files: 1/8 required = 12.5%.
- Validation: 0/5 required layers = 0%.
- Integration: 1/4 required decisions = 25% (canonical owner selected only).
- Goal activation: 5%.
- Session consolidation: 7/7 session goals durably inventoried; implementation evidence still pending.
