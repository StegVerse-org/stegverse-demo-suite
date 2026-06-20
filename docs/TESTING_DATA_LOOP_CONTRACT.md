# Testing Data Loop Contract

This repository is a downstream evaluation route. Formal testing data reaches this repository after the corrected testing data loop has produced receipt-bound artifacts.

## Required Upstream Loop

```text
User
→ StegVerse-org/StegVerse-SDK or LLM Adapter
→ StegVerse-org ingestion
→ StegGhost/entity-sandbox-runner ingestion/CGE
→ ephemeral sandbox batch
→ StegGhost/entity-sandbox-runner ingestion/CGE return validation
→ StegVerse-org ingestion
→ evaluation route
```

## Required Input Evidence

Public demo inputs preserve:

```text
sdk_or_llm_adapter_intake receipt
stegverse_org_ingestion_outbound receipt
stegghost_ingestion_cge_admission receipt
ephemeral_sandbox_batch receipt
stegghost_ingestion_cge_return_validation receipt
stegverse_org_ingestion_return receipt
master-records action receipt references
```

## Result Rule

Every demo result preserves the SDK intake manifest reference, SDK intake receipt reference, testing loop receipt-chain reference, and route-local result receipt.

SDK contract reference:

```text
StegVerse-org/StegVerse-SDK/docs/TESTING_DATA_LOOP_CONTRACT.md
```

Route result schema:

```text
StegVerse-org/StegVerse-SDK/schemas/formal-testing-route-result.schema.json
```
