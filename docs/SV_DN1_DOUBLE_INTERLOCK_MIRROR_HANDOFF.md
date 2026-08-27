# SV-DN-1 Double-Interlock Mirror Handoff

## Repository

```text
organization: StegVerse-org
repository: stegverse-demo-suite
branch: main
goal_id: DEMO-MODEL-DISTRIBUTION-NEUTRALITY-001
issue: #5
claim_state: SOURCE_MERGED_LIVE_OBSERVATION_PENDING
canonical_public_demo_owner: StegVerse-org/stegverse-demo-suite
credential_authority: TV/TVC
authority_effect: NONE
```

## Goal

Build the first public, reproducible StegVerse model-distribution neutrality and portability demonstration using the existing SDK-governed evaluator relationship and an explicitly symmetric Interlock/InTr topology.

This goal is new. It does not reopen, rewrite, or reduce the completed `DEMO-EVALUATOR-PORTABLE-001` goal.

## Source-of-truth order

Before mutation or continuation, inspect in this order:

1. `docs/SV_DN1_DOUBLE_INTERLOCK_MIRROR_HANDOFF.md`
2. issue `#5`
3. `docs/DEMO_EVALUATOR_MIRROR_HANDOFF.md`
4. `StegVerse-org/StegVerse-SDK/docs/EVALUATION_RELATIONSHIP_MIRROR_HANDOFF.md`
5. `StegVerse-Labs/StegOS/docs/UNIVERSAL_INTERLOCK_PROTOCOL_MIRROR_HANDOFF.md`
6. `StegVerse-Labs/StegCore/docs/PORTABLE_INTERLOCK_BOUNDED_TRAVERSAL_MIRROR_HANDOFF.md`
7. applicable current-main commits, open PRs, tests, result receipts, and live runtime evidence

Newer live repository/runtime evidence overrides chat summaries.

## Architectural answer

Yes: SV-DN-1 SHOULD use the Interlock/InTr lane.

The preferred topology is not a one-sided adapter that normalizes Hugging Face data only after it enters StegVerse. It is a symmetric, inspectable, two-boundary traversal:

```text
HUGGING_FACE_PUBLIC_SURFACE
-> HF_SIDE_INTERLOCK
-> HF_SEMANTIC_ENVELOPE
-> InTr
-> STEGVERSE_INTERLOCK
-> SDK manifest/receipt intake
-> SV-DN-1 evaluator
-> bounded result receipt
```

The conceptual return path is:

```text
SV-DN-1 result
-> STEGVERSE_INTERLOCK
-> InTr
-> HF_SIDE_INTERLOCK
-> HF_NATIVE_VIEW / EXTERNAL_REVIEW_VIEW
```

The far-side Interlock is a StegVerse-defined reference interlock installed or runnable at the Hugging Face-facing boundary. It is not represented as Hugging Face-owned, Hugging Face-endorsed, or Hugging Face-operated unless Hugging Face explicitly adopts or runs it.

## Why the far-side Interlock matters

Transparency is stronger when semantic transformation occurs at an explicit boundary visible to both sides.

The far-side Interlock MUST:

1. identify the exact Hugging Face source object(s);
2. preserve native identifiers and URLs/refs;
3. preserve raw source hashes where legally and technically permissible;
4. map source fields into a versioned semantic envelope;
5. identify every transformation rule used;
6. emit a transformation receipt;
7. preserve unmapped/unknown fields rather than silently discarding them;
8. distinguish raw observation from normalized semantics and inference;
9. emit no governance verdict;
10. transfer no authority.

From the Hugging Face-side point of view, the system should be inspectable as:

```text
native Hugging Face object
+ declared mapping profile
+ transformation receipt
= exact semantic packet sent through InTr
```

From the StegVerse-side point of view:

```text
semantic packet
+ far-side receipt
+ InTr traversal receipt
+ StegVerse-side intake receipt
= admissible evidence candidate
```

## Symmetric semantic boundary

The two Interlocks serve different roles but MUST share one declared exchange identity.

### HF-side Interlock

Role: `SOURCE_SEMANTIC_ADAPTER`

Allowed:
- read public/admitted source material;
- bind source identity and content hashes;
- normalize into the SV-DN-1 exchange schema;
- emit mapping and transformation evidence;
- expose unknown/unmapped fields;
- produce a far-side transition receipt.

Forbidden:
- making a StegVerse governance decision;
- rewriting source evidence without lineage;
- hiding transformations;
- asserting Hugging Face endorsement;
- using provider credentials unless separately admitted by TV/TVC;
- treating semantic conversion as truth.

### StegVerse-side Interlock

Role: `DESTINATION_ADMISSION_ADAPTER`

Allowed:
- validate the far-side envelope and receipt;
- verify source/transformation lineage;
- bind the packet to SDK intake manifest/receipt identity;
- reject malformed, incomplete, stale, replayed, or contradictory packets;
- admit bounded evidence to the SV-DN-1 evaluator.

Forbidden:
- silently changing far-side semantics;
- inferring source facts that are absent;
- granting execution or certification authority;
- collapsing unknown into pass/fail.

## Proposed exchange contract

Initial contract identifier:

`stegverse.sv-dn1.interlock-exchange/v1`

Minimum envelope:

```json
{
  "schema_version": "stegverse.sv-dn1.interlock-exchange/v1",
  "exchange_id": "<deterministic>",
  "source_system": "huggingface",
  "source_object": {
    "kind": "<model|dataset|space|api-response|other>",
    "native_id": "<exact>",
    "native_revision": "<exact-or-null>",
    "native_ref": "<exact public/admitted ref>",
    "observed_at": "<timestamp>"
  },
  "raw_evidence": {
    "content_hashes": [],
    "preserved_native_fields": {},
    "unmapped_fields": {}
  },
  "semantic_mapping": {
    "profile": "SV-DN-1-HF/v1",
    "ruleset_hash": "<sha256>",
    "transformations": [],
    "lossy_transformations": []
  },
  "far_side_receipt": {
    "interlock_role": "SOURCE_SEMANTIC_ADAPTER",
    "authority_effect": "NONE"
  },
  "intr": {
    "transport_profile": "<declared>",
    "previous_receipt_hash": "<exact>"
  }
}
```

The exchange schema and field set are implemented and source-validated on main; live external traversal remains separately unobserved.

## Semantic reversibility requirement

The mapping should be as reversible as practical.

For each normalized field, the receipt SHOULD answer:

```text
Which Hugging Face field(s) produced this value?
Which transformation rule was applied?
Was information lost?
Can the original representation be reconstructed?
If not, exactly what was lost?
```

No lossy transform may be silent.

This is important because the purpose is not merely interoperability. It is inspectable interoperability.

## No false "their end" claim

Until Hugging Face explicitly installs, runs, or adopts the far-side Interlock, public language MUST say:

- `Hugging Face-facing Interlock`
- `HF-side reference Interlock`
- `external-side semantic adapter`

Do NOT say:

- `Hugging Face's Interlock`
- `Hugging Face integrated StegVerse`
- `Hugging Face adopted InTr`

A StegVerse-controlled adapter positioned at the external boundary is still useful and transparent, but ownership/operation must remain explicit.

## Relationship to Universal Interlock

The current Universal Interlock source is merged as `SV-INTERLOCK-v0.4-candidate`, but canonical protocol adoption and runtime activation remain pending.

Therefore SV-DN-1 may implement a bounded reference-compatible profile and deterministic fixtures against the merged source semantics, but MUST NOT claim:

- canonical Universal Interlock adoption;
- production Universal Interlock runtime activation;
- authentic external runtime traversal merely from CI;
- Hugging Face-side runtime deployment.

Any authentic live traversal must be separately evidenced.

## Relationship to InTr

InTr provides the bounded transit between the two semantic boundaries.

Existing InTr evidence establishes baseline/double-Interlock source semantics and connected non-secret runtime observations in other lanes, but does not by itself prove this new Hugging Face-facing route.

SV-DN-1 MUST create route-specific receipts rather than borrowing runtime claims from unrelated provider paths.

## Relationship to SDK intake

All evaluated evidence MUST still enter through the canonical SDK evaluation relationship.

The far-side Interlock does not bypass SDK intake.

```text
HF-side Interlock
-> InTr
-> StegVerse Interlock
-> SDK manifest binding
-> SDK receipt binding
-> declared SV-DN-1 route
-> deterministic evaluator
```

This preserves the existing rule that unbound external data cannot become formal test input.

## Public observability objective

The public should be able to inspect:

1. the original Hugging Face source reference;
2. the exact far-side mapping profile;
3. the semantic packet;
4. the transformation receipt;
5. the InTr traversal identity;
6. the StegVerse-side admission receipt;
7. the SDK intake receipt;
8. the SV-DN-1 result receipt;
9. replay/reconstruction material;
10. later deltas if the Hugging Face surface changes.

That lets a third party distinguish:

```text
what Hugging Face exposed
what the adapter changed
what InTr transported
what StegVerse admitted
what SV-DN-1 evaluated
what Governance later decided
```

## Initial implementation files

Create under this goal:

```text
docs/SV_DN1_DOUBLE_INTERLOCK_MIRROR_HANDOFF.md
config/sv_dn1_profile.json
config/sv_dn1_hf_mapping.v1.json
schemas/sv-dn1-interlock-exchange.schema.json
schemas/sv-dn1-result-receipt.schema.json
stegverse_demo/sv_dn1_hf_interlock.py
stegverse_demo/sv_dn1_stegverse_interlock.py
stegverse_demo/sv_dn1_evaluator.py
scripts/run_sv_dn1.py
scripts/render_sv_dn1_report.py
fixtures/sv_dn1/
tests/test_sv_dn1_double_interlock.py
```

Exact package paths may be adjusted to current repository conventions, but all required surfaces must remain represented.

## First implementation sequence

1. inspect repo layout and current test/package conventions;
2. create the machine-readable exchange schema;
3. create HF semantic mapping profile v1;
4. implement deterministic HF-side semantic adapter;
5. implement StegVerse-side envelope validator/admission adapter;
6. bind to SDK-style intake receipt references without duplicating SDK authority;
7. implement deterministic SV-DN-1 evaluator;
8. add neutral fixtures before live network evidence;
9. add negative tests for silent loss, source substitution, stale revision, transformation tamper, mismatched exchange identity, and unknown-field suppression;
10. generate a public report from the same result receipt;
11. only then add a live public Hugging Face observation packet.

## Validation distinctions

Keep these states distinct:

```text
SCHEMA_IMPLEMENTED
MAPPING_IMPLEMENTED
SOURCE_VALIDATED
FIXTURE_VALIDATED
MERGED
LIVE_EXTERNAL_OBSERVATION
LIVE_DOUBLE_INTERLOCK_TRAVERSAL
SDK_ADMITTED
SV_DN1_EVALUATED
PUBLIC_REPORT_PUBLISHED
GOVERNANCE_MAPPED
CERTIFICATION_ELIGIBLE
CERTIFIED
```

No earlier state implies a later one.

## Cross-repository propagation

After validated implementation and live evidence, inspect and update only where pertinent:

- `StegVerse-org/StegVerse-SDK`
- `StegVerse-Labs/Governance`
- `StegVerse-Labs/StegCore`
- `StegVerse-Labs/admissibility-wiki`
- `GCAT-BCAT-Engine/Publisher`
- `StegVerse-Labs/Site`
- `StegVerse-002/stegguardian-wiki`

Do not propagate claims before the corresponding evidence exists.

## Release boundary

This goal is not release-ready until at minimum:

- schemas and mappings are versioned;
- deterministic local reproduction passes;
- transformation lineage is inspectable;
- negative/tamper cases fail closed;
- SDK intake binding is real or explicitly fixture-only;
- at least one real public Hugging Face observation is receipt-bound;
- public report can be regenerated from receipts;
- no false adoption/endorsement wording exists.

## Public dashboard posture

A public-facing dashboard is part of this goal because it makes the evaluation process observable over time rather than presenting only occasional narrative reports.

The dashboard MUST be receipt-derived and static-viewable. Target observation cadence:

```text
TWICE_DAILY_WHEN_RESIDENT_OBSERVER_AVAILABLE
PLUS_MATERIAL_DELTA
target_refresh_hours: 12
```

Benefits and constraints:

- exposes current observation time, artifact/revision, admission state, dimension results, semantic-mapping identity, lossy/unmapped counts, and receipt chain;
- makes changes over time visible without rewriting prior results;
- lets third parties distinguish a stale observation from a current one;
- gives Hugging Face or any outside reviewer the exact receipt/hash basis to challenge;
- preserves UNKNOWN rather than filling gaps for presentation;
- provides a public evidence surface even when no preference/bias is detected;
- must never turn GitHub Actions into production observation/runtime/control-plane authority;
- fixture dashboards must never be labeled live;
- a material delta may trigger a new publication before the next scheduled observation.

Current implementation adds a static HTML renderer and reserves `public/sv-dn1/` for receipt-derived output. No live public result is published yet.

## Current completion

```text
goal definition: COMPLETE
issue/task surface: COMPLETE
dedicated mirror handoff: MERGED
architecture: MERGED
SV-DN-1 profile: MERGED
HF mapping profile: MERGED
exchange schema: MERGED
result receipt schema: MERGED
HF-side semantic adapter: MERGED
StegVerse-side adapter: MERGED
evaluator: MERGED
fixture: MERGED
negative/deterministic tests: MERGED
receipt-derived markdown report renderer: MERGED
receipt-derived public dashboard renderer: MERGED
fixture pipeline runner: MERGED
validation-only workflow: MERGED
Validate SV-DN-1 run 33125102052: PASS
Architecture Guard run 33125102033: PASS
deterministic double-Interlock tests: PASS
fixture-only end-to-end pipeline: PASS
fixture/live separation: PASS
no-hosted-authority regression: PASS
source validation: PASS_AT_11949fbc3ecbc07b3c7e71a44000385c8ffb6616
merge: PR #6 MERGED
merge_commit: 65045e5b72413a9ac0242b4e865ea4ad142a4417
live Hugging Face observation: NOT OBSERVED
live double-Interlock traversal: NOT OBSERVED
SDK live admission: NOT OBSERVED
public live result: NOT PUBLISHED
governance mapping: NOT PERFORMED
release: NOT READY
```

## Live observer / dashboard-history source slice

A second source slice now exists on `feature/sv-dn1-live-observer` to make the twice-daily dashboard posture implementable without granting GitHub Actions production observation authority.

Added source surfaces:

```text
config/sv_dn1_observation_schedule.json
schemas/sv-dn1-source-capture.schema.json
scripts/observe_sv_dn1_hf_public.py
scripts/build_sv_dn1_dashboard_history.py
tests/test_sv_dn1_public_observer.py
.github/workflows/validate-sv-dn1.yml (validation-only extension)
```

Observer boundary:

- HTTPS Hugging Face hosts only;
- public JSON only;
- no Authorization header or provider credential;
- exact raw bytes are hashed before semantic normalization;
- requested and final URLs are both recorded;
- redirects leaving the Hugging Face boundary fail closed;
- response-size and content-type gates fail closed;
- source capture itself claims no live Interlock traversal, no Hugging Face endorsement, and no authority effect.

Dashboard-history boundary:

- reconstructs ordered observations from receipt directories;
- records revision changes, ruleset changes, SDK-binding changes, and per-dimension state deltas;
- never rewrites prior receipts;
- authority effect remains NONE.

The scheduled refresh target remains 12 hours plus material-delta publication. The source observer is suitable for a future admitted resident runtime; GitHub Actions only validates the source and fixture behavior.

## Next executable goal

The source implementation is merged. The next goal is a real public observation lane without changing the authority model:

1. validate and merge the implemented resident/public-source observer that captures exact Hugging Face response bytes, content type, retrieval time, source URL, and digest;
2. feed that capture into the merged HF-facing semantic Interlock;
3. obtain route-specific InTr/Interlock evidence rather than fixture-only lineage;
4. bind the resulting exchange through the canonical SDK intake path;
5. evaluate it with SV-DN-1;
6. generate the first live receipt-derived dashboard;
7. make the public dashboard refresh target 12 hours when an admitted resident observer is available, plus immediate material-delta publication;
8. only after live evidence, review propagation to Governance, Site, Publisher, admissibility-wiki, and stegguardian-wiki.

No GitHub Actions workflow is authorized to substitute for the resident external observer.

## Archive readiness

This handoff is the canonical continuation source for the SV-DN-1 double-Interlock goal. PR #6 is merged and the source lane is independently recoverable. The originating conversation is not required to recover the architecture, boundaries, merged source files, validation evidence, or next executable goal.
