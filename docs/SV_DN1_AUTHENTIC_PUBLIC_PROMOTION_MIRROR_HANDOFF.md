# SV-DN-1 Authentic Public Promotion Mirror Handoff

Updated: 2026-08-30
Repository: `StegVerse-org/stegverse-demo-suite`
Goal: `DEMO-SV-DN1-AUTHENTIC-PUBLIC-PROMOTION-001`
Parent handoffs:
- `docs/SV_DN1_PUBLIC_DASHBOARD_DEPLOYMENT_MIRROR_HANDOFF.md`
- `docs/SV_DN1_LIVE_SDK_RESULT_BINDING_MIRROR_HANDOFF.md`
- `docs/SV_DN1_DOUBLE_INTERLOCK_MIRROR_HANDOFF.md`

## Goal

Provide the missing fail-closed transition from an already-authentic, already-finalized SV-DN-1 first-round result into the checked-in static public projection consumed by the existing Pages deployment lane.

The promotion stage is projection only:

```text
authentic finalized result directory
  first-round-analysis.json
  production-pipeline-observation.json
  result-receipt.json
  report.md
  index.html
        ↓
independent coherence validation
        ↓
copy exact finalized bytes into public/sv-dn1/
        ↓
emit local promotion receipt
        ↓
repository mutation/review/merge as a separate source lifecycle event
        ↓
existing static Pages deployment
```

## Authority boundary

The promoter MUST NOT:
- fetch Hugging Face or any evaluated source;
- execute the evaluator or SDK;
- perform SDK admission;
- alter governance disposition;
- perform Master Records custody/replay/reconstruction;
- synthesize result fields;
- rewrite the dashboard/report/result semantics;
- decide a new publication state;
- grant repository mutation, release, deployment, runtime, credential, governance, or certification authority.

The promoter may only validate that the finalized artifact set is internally coherent and already carries a non-`WITHHELD` live publication state, then copy the exact bytes into `public/sv-dn1/`.

Credential authority remains `TV/TVC`. Promotion itself requires no credential and has `authority_effect=NONE_STATIC_PROJECTION_ONLY`.

## Required input predicates

`first-round-analysis.json` must prove:
- `schema_version=stegverse.sv-dn1.first-round-analysis/v1`
- `state=ANALYZED`
- `profile_id=SV-DN-1`
- `claims.first_round_analyzed=true`
- `claims.dashboard_generated=true`
- `claims.dashboard_publicly_hosted=false`
- `claims.certification_claimed=false`
- `claims.production_perfection_claimed=false`
- `authority_effect=NONE`

`production-pipeline-observation.json` must prove:
- `observation_class=LIVE`
- `publication_state != WITHHELD`
- exact `exchange_id` continuity with the analysis and result receipt

`result-receipt.json` must prove:
- exact `receipt_id` continuity with `analysis.external_evaluation.result_receipt_id`
- exact `exchange_id` continuity with the analysis

The artifact map in the analysis must name exactly the expected finalized output files.

## Exact-byte rule

Promotion must copy the finalized bytes unchanged. The promoter computes SHA-256 for every source artifact and verifies the destination hash is identical after copy. It does not render a new dashboard or report.

## Output

A successful local promotion emits a receipt outside the public surface by default:

```text
schema: stegverse.sv-dn1.public-promotion-receipt/v1
state: PROMOTION_READY_FOR_REPOSITORY_MUTATION
profile_id: SV-DN-1
publication_state: <already-finalized state>
observation_class: LIVE
source_artifact_sha256: {...}
destination_artifact_sha256: {...}
exact_bytes_preserved: true
semantic_rewrite_performed: false
network_fetch_performed: false
credential_used: false
repository_writeback_performed: false
deployment_performed: false
authority_effect: NONE_STATIC_PROJECTION_ONLY
```

`repository_writeback_performed=false` is required because the script itself only mutates the local checkout. A later repository commit/merge is separate evidence and must not be conflated with runtime analysis or Pages deployment.

## Public destination

```text
public/sv-dn1/index.html
public/sv-dn1/first-round-analysis.json
public/sv-dn1/production-pipeline-observation.json
public/sv-dn1/result-receipt.json
public/sv-dn1/report.md
```

The initial `WITHHELD` placeholder remains until an authentic finalized result satisfies every predicate above.

## Validation requirements

Tests must prove:
- authentic live finalized artifact set promotes exact bytes;
- `WITHHELD` input fails closed;
- non-`ANALYZED` input fails closed;
- mismatched exchange identity fails closed;
- mismatched result receipt identity fails closed;
- unexpected/missing artifact map fails closed;
- source/destination hashes match exactly;
- no network/credential/repository/deployment authority is claimed.

## Runtime truth

At handoff creation:

```text
Hugging Face resident observation: OBSERVED
Universal InTr hop: OBSERVED
SDK first production round: NOT YET AUTHENTICALLY ANALYZED
promotion handoff: IMPLEMENTED
promotion script: NOT YET IMPLEMENTED
promotion tests: NOT YET IMPLEMENTED
public live result: NOT YET PUBLISHED
Pages static hosting lane: IMPLEMENTED / PREVIOUSLY DEPLOYED
```

Newer authentic runtime evidence overrides this handoff.
