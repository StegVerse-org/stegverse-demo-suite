# Hugging Face Acquisition-Drift Public Analysis Mirror Handoff

Updated: 2026-09-02
Repository: StegVerse-org/stegverse-demo-suite
Goal ID: HF-ACQUISITION-DRIFT-001
Status: IMPLEMENTATION_STARTED
Primary evidence substrate: SV-DN-1

## Source of truth

This file is the canonical handoff for the public-facing longitudinal analysis of Hugging Face after its announced acquisition by Nvidia.

## Research question

Determine whether Hugging Face's observable business model, product priorities, access model, governance posture, or community orientation measurably drift after acquisition in ways that disadvantage or de-prioritize the open-source/open-weight audience that materially contributed to the platform's growth.

This analysis is observational. It does not infer motive from a single event and does not treat acquisition as proof of future drift.

## Separation from SV-DN-1

SV-DN-1 remains the governed source-observation and evidence-transport substrate.

This lane consumes receipt-bound observations and computes longitudinal public-analysis outputs. It MUST NOT rewrite SV-DN-1 evidence or turn narrative interpretation into source fact.

Canonical relationship:

```text
Hugging Face public surface
-> SV-DN-1 source capture / semantic Interlock / InTr
-> receipt-bound observation history
-> HF acquisition-drift feature extraction
-> longitudinal comparison
-> bounded public findings
```

## Baseline and comparison windows

The analysis must preserve a pre-acquisition baseline and compare it against post-acquisition observations.

Required window labels:
- PRE_ACQUISITION_BASELINE
- TRANSITION_WINDOW
- POST_ACQUISITION_EARLY
- POST_ACQUISITION_ESTABLISHED

Window boundaries must be explicit and versioned in analysis outputs.

## Core observable dimensions

1. Community access
   - public model/dataset/space accessibility
   - gating/private-status changes
   - API accessibility
   - rate/usage restrictions
   - authentication requirements

2. Commercial model
   - pricing changes
   - paid-tier expansion
   - enterprise feature prioritization
   - previously free capability restrictions

3. Ecosystem neutrality
   - hardware/vendor neutrality
   - preferential integration signals
   - discoverability/ranking shifts
   - dependency or hosting preference shifts

4. Open-source/open-weight orientation
   - treatment of community projects
   - public repository/model visibility
   - licensing metadata availability
   - support for independent model distribution

5. Governance/transparency posture
   - public incident disclosure
   - policy/documentation changes
   - moderation/access rule changes
   - transparency of removals, restrictions, or platform interventions

6. Security and adversarial-event surface
   - publicly disclosed intrusions or exploitation
   - unauthorized agent/tool activity visible at the platform boundary
   - mitigations that alter community access or platform openness
   - whether security response introduces durable asymmetry between enterprise and community users

Security incidents are evidence dimensions, not the primary thesis.

## Evidence classes

Every observation must be classified as one of:
- DIRECT_PUBLIC_OBSERVATION
- RECEIPT_BOUND_SV_DN1_OBSERVATION
- OFFICIAL_ANNOUNCEMENT
- THIRD_PARTY_REPORT
- INFERENCE
- UNKNOWN

No inference may be emitted as a direct observation.

## Drift findings

Allowed finding states:
- NO_MATERIAL_DRIFT_OBSERVED
- MIXED_DRIFT
- COMMUNITY_NEGATIVE_DRIFT
- COMMUNITY_POSITIVE_DRIFT
- INSUFFICIENT_EVIDENCE

Each finding must include:
- window
- dimension
- evidence references
- direction
- confidence
- contradictory evidence
- unresolved unknowns

## Security / hack observation extension

The lane may record public incidents and attempted attacks only insofar as they reveal:
- changed access constraints;
- changed transparency;
- changed platform architecture;
- changed trust boundaries;
- changed moderation or governance;
- changed treatment of community users;
- evidence of vendor-specific prioritization.

It MUST NOT convert a security event alone into a business-model drift finding.

## Public reporting principle

The public output should answer:

```text
What changed?
When did it change?
Which user/community group is affected?
What direct evidence supports that?
What alternative explanation remains plausible?
Is the change persistent or temporary?
```

## Immediate implementation files

- `docs/HF_ACQUISITION_DRIFT_MIRROR_HANDOFF.md`
- `config/hf_acquisition_drift_profile.json`

Next machine implementation:
- schema for normalized longitudinal observations;
- deterministic drift classifier;
- baseline snapshot materialization;
- receipt-derived timeline renderer;
- public report/dashboard integration;
- tests for evidence/inference separation and contradictory evidence.

## Cross-repository propagation when findings become publishable

Inspect and update only if pertinent:
- StegVerse-Labs/Site
- GCAT-BCAT-Engine/Publisher
- StegVerse-Labs/admissibility-wiki
- StegVerse-002/stegguardian-wiki

Do not propagate acquisition-drift claims before receipt-bound evidence exists.
