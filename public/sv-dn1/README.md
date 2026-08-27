# SV-DN-1 Public Dashboard Surface

This directory is reserved for receipt-derived public dashboard output.

Generate the dashboard with:

    python scripts/render_sv_dn1_dashboard.py \
      --exchange <exchange.json> \
      --receipt <result-receipt.json> \
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
