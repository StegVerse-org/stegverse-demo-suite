# Governed Digital Rights Mirror Handoff

## Canonical identity
- Active goal ID: `GDRC-DEMO-001`
- Active goal: Install and validate the smallest public demonstration of governed digital-rights continuity for royalty-bearing media.
- Originating session goal: Demonstrate how governed AI can track ownership, authority transitions, usage, royalty allocation, and historical reconstruction for songs, albums, movies, and related digital products.
- Repository: `StegVerse-org/stegverse-demo-suite`
- Branch: `feat/governed-digital-rights-demo`
- Pull request: `StegVerse-org/stegverse-demo-suite#1`
- Canonical handoff: `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md`
- Canonical task owner: `StegVerse-org/stegverse-demo-suite`

## Active claims
| Task ID | Claim state | Role | Claimant | Exact surfaces | Created | Expiration / release condition | Expected evidence |
|---|---|---|---|---|---|---|---|
| GDRC-DEMO-001 | CLAIMED_FOR_INTEGRATION | hosted validation + merge | `chatgpt-session-2026-08-03-gdrc` | PR #1 and the eight canonical files listed below | 2026-08-03T18:19:00-05:00 | Release on merged PR, explicit transfer, or 2026-08-04T18:19:00-05:00 if no new evidence-bearing commit or run appears | inspected workflow jobs, receipt artifact, merge commit |
| GDRC-PROP-001 | CLAIMED_FOR_INTEGRATION | propagation assessment | `chatgpt-session-2026-08-03-gdrc` | Site, Publisher, admissibility-wiki, stegguardian-wiki, master-records handoffs/contracts | 2026-08-03T18:19:00-05:00 | Release after the canonical demo is merged and each destination is classified as required, not required, or blocked with an exact durable owner | destination commit, issue, or explicit no-propagation decision |

Collision boundary: no open issue, pull request, branch search result, or repository task containing `royalty`, `rights`, `ownership`, `song`, or `digital` was found before claim creation. This claim does not authorize changes to SDK intake, kernel authority, payout execution, external collecting-society systems, or production payment rails.

## Authoritative files
1. `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md`
2. `demos/governed_digital_rights/README.md`
3. `demos/governed_digital_rights/demo_case.json`
4. `demos/governed_digital_rights/task_state.json`
5. `demos/governed_digital_rights/validate_demo.py`
6. `demos/governed_digital_rights/test_validate_demo.py`
7. `schemas/governed_digital_rights_demo.schema.json`
8. `.github/workflows/governed-digital-rights-demo.yml`

Repository boundary source: `README.md` defines this repository as the public reproducible demonstration layer after SDK ingestion, manifest binding, and receipt binding. The demo does not bypass that route.

## Session goal inventory
| Task ID | Originating goal | Exact destination | Owner | Claim state | Completion | Validation | Integration | Archival dependency | Evidence | Next executable action |
|---|---|---|---|---|---|---|---|---|---|---|
| GDRC-DEMO-001 | One fictional song, three participants, two usage periods | eight canonical files in PR #1 | demo-suite | CLAIMED_FOR_INTEGRATION | implemented | local pass; hosted pending | PR open | yes | commits `2722f39` through `ef75cb3`; local receipt hash below | inspect hosted run for latest PR head |
| GDRC-AUTH-001 | Deny unilateral label increase | fixture + evaluator + tests | demo-suite | COMPLETE | complete | deterministic `DENY`; test pass | included in PR #1 | no after merge | `MISSING_REQUIRED_SIGNATURES` | none unless hosted run fails |
| GDRC-TIME-001 | Apply unanimous amendment prospectively | fixture + evaluator + tests | demo-suite | COMPLETE | complete | old/new period assertions pass | included in PR #1 | no after merge | `AUTHORIZED_NON_RETROACTIVE_AMENDMENT` | none unless hosted run fails |
| GDRC-RECON-001 | Reconstruct historical rights and allocation | evaluator receipt | demo-suite workflow | MACHINE_OWNED | locally complete | receipt hash verified locally | artifact pending | yes | `e2172b505ec9978513d5143858b55abf0cfbd935a6adb8b852cdd6cf8d6fa784` | inspect uploaded workflow artifact |
| GDRC-AUTO-001 | Automate tests, receipt, and stale-claim visibility | workflow + task state | GitHub Actions | MACHINE_OWNED | installed | workflow run pending | PR trigger installed | yes | `.github/workflows/governed-digital-rights-demo.yml` | observe PR synchronization run |
| GDRC-PROP-001 | Determine Site/Publisher/wiki/master-records propagation | destination handoffs or issues | current integration claimant | CLAIMED_FOR_INTEGRATION | not started | pending | pending | yes | this handoff | inspect destination handoffs after hosted evidence exists |
| GDRC-STANDARD-001 | Preserve expansion path for albums, films, publishing, images, games, datasets, AI-training permissions | this handoff | canonical workstream | MERGED_INTO_CANONICAL_WORKSTREAM | requirements transferred, not activated | not applicable | bounded roadmap only | no | design decisions below | activate only through a separately claimed extension |

## Design decisions transferred from the session
1. The smallest presentation is one fictional song, three rights participants, one unauthorized ownership mutation, and one properly authorized future-effective amendment across two usage periods.
2. Rights state is not a single owner field. The fixture records asset identity, component hashes, participants, shares, authority, effective time, usage, policy, allocation, attempted mutation, accepted amendment, and reconstruction evidence.
3. AI may interpret and reconcile records, but signed authority declarations, policy references, and receipts remain the source of truth.
4. Historical state is immutable: a later amendment cannot retroactively change an earlier allocation.
5. Invalid transitions remain visible as denied events.
6. Public demo evidence does not assert legal title, external platform integration, collecting-society recognition, payment settlement, endorsement, or production authority.
7. Presentation title/question: `Who Gets Paid—and Can the Answer Be Proven?`

## Implemented scenario
- Initial split: artist/songwriter 50%, producer 25%, label/publisher 25%.
- Period 1: 10,000 streams and USD 100.00 distributable; allocation USD 50.00 / 25.00 / 25.00.
- Unauthorized label-only increase to 40%: `DENY — MISSING_REQUIRED_SIGNATURES`.
- Unanimous amendment effective after period 1: `ALLOW — AUTHORIZED_NON_RETROACTIVE_AMENDMENT`.
- New split: artist 40%, producer 35%, label 25%.
- Period 2: USD 40.00 / 35.00 / 25.00.

## Validation evidence
Local deterministic execution on 2026-08-03:

```bash
python -m unittest discover -s demos/governed_digital_rights -p 'test_*.py' -v
# Ran 9 tests: OK

python demos/governed_digital_rights/validate_demo.py \
  --input demos/governed_digital_rights/demo_case.json \
  --schema schemas/governed_digital_rights_demo.schema.json \
  --task-state demos/governed_digital_rights/task_state.json \
  --output build/governed-digital-rights/receipt.json
# status COMPLETE
# receipt_sha256 e2172b505ec9978513d5143858b55abf0cfbd935a6adb8b852cdd6cf8d6fa784
```

Validated locally:
- JSON parsing and committed schema-document binding;
- exact participant-set equality;
- 10,000-basis-point conservation;
- chronological rights reconstruction;
- unanimous signature authority;
- non-retroactivity;
- deterministic largest-remainder allocation;
- royalty conservation;
- expected-decision matching;
- receipt hash determinism;
- stale-claim observability.

Hosted state at PR creation: no pull-request workflow run or commit status was yet returned for head `ef75cb33cd1ffd539dd82bc3a0082c51fdc54dc9`. This handoff update is an evidence-bearing synchronization commit intended to trigger the installed pull-request workflow. Release condition: a run associated with the latest PR head becomes inspectable, or the absence is recorded as BLOCKED with GitHub Actions as owner and an exact repository setting/run condition.

## Automation contract
- Owner repository: `StegVerse-org/stegverse-demo-suite`.
- Trigger: pull request, push, or manual dispatch when canonical files change.
- Deterministic inputs: fixture, schema, evaluator, tests, task state.
- Outputs: test result, `COMPLETE` JSON receipt, SHA-256 verification, uploaded artifact.
- Persistent state: Git history, PR #1, workflow run, artifact, this handoff.
- Fail closed on missing evidence, malformed shares, unauthorized signatures, retroactivity, expectation mismatch, allocation mismatch, or hash mismatch.
- States recognized: COMPLETE, BLOCKED, RETRY, REVIEW_REQUIRED, FAILED, CLAIMED, SUPERSEDED, MERGED.
- Collision control: task ID plus exact path claim.
- Stale claim: machine-observable after `2026-08-04T23:19:00Z` while state remains CLAIMED.

## Integration and propagation obligations
- SDK intake is an architectural prerequisite for formal production input, not a blocker to a bounded committed public fixture.
- Do not claim Site, Publisher, admissibility-wiki, stegguardian-wiki, or master-records propagation until destination handoffs/contracts are inspected and destination evidence exists.
- If a destination already has a canonical owner for public demo publication or admissibility evidence, transfer only the missing reference to PR #1 and this handoff; do not duplicate the evaluator.

## Completion and archive conditions
The originating session is archive-safe only after:
1. PR #1 has an inspected workflow job and receipt artifact;
2. PR #1 is merged or explicitly transferred to a durable integration owner;
3. implementation claim is released or converted to COMPLETE/MERGED;
4. propagation obligations are completed or installed as exact durable destination tasks with machine-observable release conditions;
5. final evidence and percentages are recorded here.

## Current percentages
- Task completion: 5/7 inventory items complete or durably transferred = 71%.
- Developed files: 8/8 = 100%; scaffolding/stubs: 0.
- Validation: 3/5 layers = 60% (static/semantic, unit, local deterministic complete; hosted workflow and artifact inspection pending).
- Integration: 2/4 = 50% (canonical owner and PR complete; merge and propagation pending).
- Goal activation: 65%.
- Session consolidation: 7/7 goals transferred into this handoff; archival remains blocked by hosted evidence, merge/transfer, and propagation disposition.
