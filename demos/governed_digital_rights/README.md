# Governed Digital Rights Continuity Demo

**Presentation question:** Who gets paid—and can the answer be proven?

This is the smallest bounded demonstration of governed digital-rights continuity in the StegVerse public demo layer. It uses one fictional song, three participants, two usage periods, one unauthorized ownership mutation, and one authorized future-effective amendment.

## What it proves

1. Asset identity and component hashes are explicit.
2. Initial rights shares sum to 100%.
3. A label cannot unilaterally increase its share when unanimous authorization is required.
4. A properly signed amendment can become effective prospectively.
5. The earlier royalty period remains governed by the rights state that was valid when its usage occurred.
6. Each calculation is deterministic and bound to a canonical SHA-256 receipt.
7. A stale implementation claim is machine-observable rather than silently treated as success.

## What it does not prove

This demo does not establish legal title, register copyright, integrate with a collecting society, verify real streaming reports, move funds, recognize external endorsements, or grant production execution authority. The repository remains a public demonstration layer after governed ingestion and receipt binding.

## Scenario

| Event | Result |
|---|---|
| Initial split | Artist 50%, producer 25%, label 25% |
| Period 1 | 10,000 streams and USD 100.00 distributable: USD 50 / 25 / 25 |
| Label-only amendment to 40% | `DENY — MISSING_REQUIRED_SIGNATURES` |
| Unanimous future amendment | `ALLOW — AUTHORIZED_NON_RETROACTIVE_AMENDMENT` |
| New split | Artist 40%, producer 35%, label 25% |
| Period 2 | USD 40 / 35 / 25 |

## Run

```bash
python demos/governed_digital_rights/validate_demo.py \
  --input demos/governed_digital_rights/demo_case.json \
  --schema schemas/governed_digital_rights_demo.schema.json \
  --task-state demos/governed_digital_rights/task_state.json \
  --output build/governed-digital-rights/receipt.json

python -m unittest discover \
  -s demos/governed_digital_rights \
  -p 'test_*.py' \
  -v
```

The evaluator uses only the Python standard library. The JSON Schema document is committed as the interchange contract; the evaluator also performs fail-closed semantic checks that JSON Schema alone cannot express, including exact participant-set equality, 10,000-basis-point conservation, chronological application, signature authority, expectation matching, and royalty conservation.

## Canonical continuation

See `docs/GOVERNED_DIGITAL_RIGHTS_MIRROR_HANDOFF.md` for task ownership, claim expiration, evidence, propagation obligations, and archival conditions.
