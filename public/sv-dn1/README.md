# SV-DN-1 Public Dashboard Surface

This directory is reserved for receipt-derived public dashboard output.

Generate the dashboard with:

    python scripts/render_sv_dn1_dashboard.py \
      --exchange <exchange.json> \
      --receipt <result-receipt.json> \
      --pipeline-observation <production-pipeline-observation.json> \
      --output public/sv-dn1/index.html

The dashboard is static and requires no JavaScript or live StegVerse connection to inspect.

Target public refresh posture:

    TWICE_DAILY_WHEN_RESIDENT_OBSERVER_AVAILABLE
    PLUS_MATERIAL_DELTA

A refresh cadence is an observation policy, not runtime authority. GitHub Actions MUST NOT become the production observer, provider authority, governance authority, or durable control plane merely to update this page.

Until a real public Hugging Face observation has been admitted through the route, no generated fixture dashboard should be presented as a live result.

Public wording must preserve:

- Hugging Face-facing/reference Interlock, not "Hugging Face's Interlock";
- evaluation != enforcement;
- UNKNOWN != PASS/FAIL;
- no external endorsement claim;
- no certification claim unless separately earned and evidenced.


## Production self-evaluation

SV-DN-1 is not only a public evaluation of the external subject. The active StegVerse production governance stack performing the evaluation is also an observed subject.

The public surface MUST expose the production path actually used:

    external_source_capture
    -> hf_facing_interlock
    -> intr
    -> stegverse_interlock
    -> sdk_ingress
    -> stegcore_steggate
    -> master_records_custody
    -> reconstruction
    -> public_projection

Each lane is represented independently as one of:

    PASS
    FAIL
    DEGRADED
    UNKNOWN
    NOT_REACHED
    NOT_OBSERVED
    NOT_APPLICABLE

The governing public-readiness rule is:

    PUBLIC_READINESS_REQUIRES_BOUNDED_OBSERVABLE_IMPERFECTION_NOT_PERFECTION

Production status is not a claim of correctness or completeness. A real production lane may be publicly shown as FAIL, DEGRADED, or UNKNOWN when the condition is explicit, evidence-backed, and reconstructable.

The page MUST distinguish:

- a failure or limitation in the external subject;
- a failure or limitation in StegVerse observation;
- a failure or limitation in semantic transformation;
- a failure or limitation in InTr/Interlock traversal;
- an SDK or governance rejection;
- a custody/reconstruction failure;
- a public-projection defect.

Known failures must not be hidden to improve presentation. UNKNOWN must not be promoted. A fixture must never be presented as a live production observation.

Publication posture is explicit:

    WITHHELD
    PUBLIC_WITH_LIMITATIONS
    PUBLIC_OBSERVED

`PUBLIC_WITH_LIMITATIONS` is valid when a real run contains known, bounded, evidence-backed defects or unknowns. It is not valid when execution has not reached a required production boundary, evidence lineage is ambiguous, custody/reconstruction is absent where required, fixture/live identity is confused, or an authority claim exceeds the evidence.

The demo suite renders this evidence. It does not become StegCore, StegGate, SDK, Interlock, InTr, Master Records, certification, or publication authority by displaying it.
