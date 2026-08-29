# SV-DN-1 SDK Live Admission Mirror Handoff

## Scope

```text
goal_id: DEMO-SV-DN1-SDK-LIVE-ADMISSION-002
repository: StegVerse-org/stegverse-demo-suite
branch: main
parent_goal: DEMO-MODEL-DISTRIBUTION-NEUTRALITY-001
parent_handoff: docs/SV_DN1_DOUBLE_INTERLOCK_MIRROR_HANDOFF.md
upstream_runtime_task: StegVerse-Labs/.github/SV-DN1-RESIDENT-OBSERVER-001
downstream_ingress_owner: StegVerse-org/StegVerse-SDK
credential_authority: TV/TVC
authority_effect: NONE
```

## Goal

Prepare the exact source-side bridge required after the sovereign resident observer produces an authentic SV-DN-1 source capture and HF-facing semantic exchange.

The bridge converts those already-produced evidence objects into a canonical `stegverse.ingress-manifest.v1` for the SDK 0B path without reimplementing SDK governance, fabricating admission, or promoting fixture evidence to live evidence.

## Source of truth order

1. `docs/SV_DN1_SDK_LIVE_ADMISSION_MIRROR_HANDOFF.md`
2. `docs/SV_DN1_DOUBLE_INTERLOCK_MIRROR_HANDOFF.md`
3. `tasks/SV-DN1-RESIDENT-OBSERVER-001.json`
4. `StegVerse-Labs/.github/docs/SV_DN1_RESIDENT_OBSERVER_MIRROR_HANDOFF.md`
5. `StegVerse-org/StegVerse-SDK/SDK_MIRROR_HANDOFF.md`
6. `StegVerse-org/StegVerse-SDK/stegverse/governance_navigation.py`
7. `StegVerse-org/StegVerse-SDK/stegverse/governance_ingress_runtime.py`
8. `StegVerse-org/StegVerse-SDK/stegverse/route_resolution.py`

Live repository/runtime evidence overrides older chat claims.

## Canonical SDK route facts

The SDK 0B lane is already installed. This bridge MUST target the existing published route and MUST NOT invent another evaluator or route:

```text
manifest_profile: stegverse.ingress-manifest.v1
manifest_profile_version: "1"
route_id: stegverse.route.canonical-governed.v1
lane_class: PRODUCTION_VALIDATION
routing_surface: CANONICAL_PRODUCTION
containment: PRODUCTION_ROUTE_BOUNDED_CONSEQUENCE
sandbox_required: false
external_consequence_enabled: false
```

Required SDK extensions:

```text
extensions.stegverse_route
extensions.stegverse_governance_request
```

The candidate embedded in the governance request MUST be identical to the manifest candidate under canonical hashing.

## Admission boundary

This repository may create an **SDK ingress candidate manifest**. It may not claim that the SDK has admitted it.

Required state distinction:

```text
RESIDENT_SOURCE_CAPTURE_COMPLETE
-> SDK_0B_MANIFEST_PREPARED
-> SDK_0B_MANIFEST_VALIDATED
-> SDK_0B_GOVERNED_RUN_EXECUTED
-> SDK_ADMITTED
-> SV_DN1_LIVE_RESULT_BOUND
```

Only the SDK/runtime owner may establish the governed-run/admission states.

## Required live evidence

The generator must refuse input unless all of the following are true:

- resident receipt state is `COMPLETE`;
- transition is `SV_DN1_RESIDENT_SOURCE_CAPTURE_COMPLETE`;
- `raw_response_sha256_present=true`;
- `semantic_exchange_valid=true`;
- `credential_used=false`;
- `github_token_used=false`;
- `repository_writeback_performed=false`;
- `sdk_admitted=false` at this pre-admission boundary;
- source capture claims no Hugging Face endorsement;
- exchange validates against the canonical SV-DN-1 destination validator;
- source capture and exchange refer to the same observed source identity.

Fixture-only evidence is prohibited.

## Candidate semantics

The candidate is a non-side-effect evaluation request:

```text
actor_class: sv_dn1_public_evaluator
action: evaluate_model_distribution_neutrality
target: exact Hugging Face model identity + revision
scope: public_distribution_observation
external_side_effect: false
```

The request must preserve:

- raw source digest;
- exchange id;
- semantic mapping profile and ruleset hash;
- source revision;
- transformation receipt hash;
- resident observer receipt identity;
- UNKNOWN as unresolved evidence rather than a negative or positive assertion.

## Governance request posture

The bridge does not decide the Governance outcome. It supplies bounded state for canonical SDK/StegGate evaluation.

Judgment:
- refusal/review remains available;
- workload is bounded;
- no time pressure;
- evidence references point only to exact resident capture/exchange.

Signal:
- exact admitted signal references;
- source transformation lineage;
- missing inputs explicitly retained;
- reconstruction available only where the evidence chain supports it;
- transformation provenance complete must be proven, not assumed.

Execution:
- external consequence disabled;
- no credentialed operation;
- current evidence/route predicates represented only from exact live receipts;
- policy/delegation references are non-authorizing SV-DN-1 evaluation declarations.

## Initial implementation files

```text
docs/SV_DN1_SDK_LIVE_ADMISSION_MIRROR_HANDOFF.md
schemas/sv-dn1-sdk-ingress-candidate.schema.json
scripts/build_sv_dn1_sdk_ingress_manifest.py
scripts/validate_sv_dn1_sdk_ingress_candidate.py
tests/test_sv_dn1_sdk_live_admission.py
```

## Non-claims

This source slice does not claim:

- resident observer activation unless an authentic receipt is supplied;
- live InTr traversal;
- SDK admission;
- StegGate ALLOW;
- Master Records custody;
- live dashboard publication;
- Hugging Face adoption or endorsement;
- certification.

## Current state

```text
parent SV-DN-1 source: MERGED
sovereign resident observer source/registration: MERGED
resident observer runtime receipt: NOT OBSERVED
SDK 0B canonical path: INSTALLED BY SDK OWNER
SV-DN-1 SDK manifest bridge: MERGED
SDK ingress candidate schema: MERGED
SDK-compatible source validator: MERGED
deterministic bridge tests: MERGED
validation workflow integration: MERGED
source validation: PASS
Validate SV-DN-1 run 33127803224 / job 98709998295: PASS
Architecture Guard run 33127803215 / job 98709998382: PASS
validated_head: f99e24ac1dd0d5aa1075d796e29cef040c1d849b
merge: PR #9 MERGED
merge_commit: 443f228873e34b9ed67c309dc71622703e4b51bf
final_validated_head: 3fd2b4982d608e80ea2c15a35f882442c073fafa
Validate SV-DN-1 run 33127829478 / job 98710081154: PASS
Architecture Guard run 33127829492 / job 98710081238: PASS
SDK governed execution: NOT OBSERVED
SDK live admission: NOT OBSERVED
```

## Implemented source surfaces

```text
schemas/sv-dn1-sdk-ingress-candidate.schema.json
scripts/build_sv_dn1_sdk_ingress_manifest.py
scripts/validate_sv_dn1_sdk_ingress_candidate.py
tests/test_sv_dn1_sdk_live_admission.py
.github/workflows/validate-sv-dn1.yml
```

The builder enforces the authentic resident receipt boundary before it can create an SDK 0B candidate. The local validator checks current SDK manifest/profile/hash/route semantics but explicitly does not claim that the SDK itself validated or admitted the packet.

The generated governance request preserves the still-missing runtime inputs:

```text
route_specific_intr_runtime_receipt
sdk_live_admission_receipt
```

and therefore does not manufacture a completed live path.

## Executable-precondition correction

Live comparison against the current canonical SDK/StegCore contracts exposed three source defects in the original bridge that would have prevented a real 0B governed run even after resident capture:

1. `sdk_live_admission_receipt` was incorrectly represented as a pre-execution `signal.missing_inputs` item even though it is a post-execution output.
2. `signal.uncertainty_state` used `open`, while canonical StegCore accepts only `bounded`, `material`, or `unknown`.
3. `signal.transformations` carried structured objects, while the canonical StegGate request model accepts a list of string transformation references.

The corrected bridge now distinguishes:

```text
resident capture present + no route-specific InTr receipt
-> execution_readiness=BLOCKED_ON_ROUTE_SPECIFIC_INTR
-> missing_inputs=[route_specific_intr_runtime_receipt]
-> uncertainty_state=material
-> no SDK execution claim

resident capture + valid route-specific InTr receipt
-> execution_readiness=READY_FOR_SDK_0B
-> missing_inputs=[]
-> uncertainty_state=bounded
-> continuity.previous_receipt_verified=true
-> continuity.previous_receipt_hash=<exact InTr receipt hash>
-> still no SDK admission claim until canonical SDK runtime returns
```

The route-specific receipt contract is:

```text
schema: stegverse.sv-dn1.intr-runtime-receipt/v1
route_id: SV-DN-1-HF-PUBLIC
state: COMPLETE
authority_effect: NONE
canonical_protocol_adopted: false
production_interlock_runtime_activated: false
sdk_admitted: false
```

This intentionally permits authentic route-specific evaluation traversal without falsely promoting the Universal Interlock candidate to canonically adopted or globally activated status.

Implemented on this slice:

```text
schemas/sv-dn1-intr-runtime-receipt.schema.json
scripts/build_sv_dn1_sdk_ingress_manifest.py
scripts/validate_sv_dn1_sdk_ingress_candidate.py
tests/test_sv_dn1_sdk_live_admission.py
```

## Executable-precondition merge evidence

```text
PR #13: MERGED
merge_commit: dc9a62134dd313a5ffea97ebe47ecccc6f5e9580
validated_head: b209630c145305abe644da497fd48a9c9b111157
Validate SV-DN-1 run 33129455716 / job 98715309668: PASS
Architecture Guard run 33129455739 / job 98715309723: PASS
```

The SDK bridge is now source-valid against the current canonical StegGate request model and can become `READY_FOR_SDK_0B` when an authentic route-specific InTr receipt is supplied. This is still not an SDK governed-run or admission receipt.

## Archive readiness

Once this scoped handoff and implementation are merged, the remaining runtime boundary is recoverable without this conversation.


## Universal InTr SDK-ingress reconciliation — 2026-08-29

PR #407 in `StegVerse-Labs/.github` canonically adopted
`STEGVERSE-UNIVERSAL-INTR-TRANSPORT-001`. The prior SDK precondition language
requiring a pre-adoption route-specific receipt is superseded.

`READY_FOR_SDK_0B` now requires an authentic SV-DN-1 InTr receipt representing
the adjacent hop:

```text
EXTERNAL_SYSTEM -> STEGOS_ECOSYSTEM
transport_profile: stegverse.universal-intr.adjacent-hop/v1
canonical_protocol_adopted: true
universal_intr_policy_id: STEGVERSE-UNIVERSAL-INTR-TRANSPORT-001
interlock_required_per_hop: true
receipt_hash_chain_required: true
runtime_activation_claimed: false
production_interlock_runtime_activated: false
sdk_admitted: false
authority_effect: NONE
```

The builder and validator still reject credential use, authority transfer,
receipt/hash mismatch, premature SDK admission, global runtime-activation
claims, and external endorsement. Canonical policy adoption is a fact reported
by the receipt; it is not authority granted by the receipt.
