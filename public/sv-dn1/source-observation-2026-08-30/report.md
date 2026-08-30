# SV-DN-1 Live Hugging Face Source Observation — 2026-08-30

This is a public analysis of live Hugging Face metadata for `Qwen/Qwen3-8B`. It is intentionally separate from the governed SV-DN-1 first production round, which remains `WITHHELD` until the canonical SDK / StegCore / Master Records chain produces authentic receipt-bound evidence.

## Source

- Provider: Hugging Face
- Endpoint: `https://huggingface.co/api/models/Qwen/Qwen3-8B`
- Model: `Qwen/Qwen3-8B`
- API revision SHA: `b968826d9c46dd6066d109eabc6255188de91218`
- Observed: `2026-08-30T17:15:00Z`

## Observed metadata

The repository is public, non-gated, and enabled. Hugging Face classifies it as a text-generation model using Transformers, with `Qwen3ForCausalLM` / `qwen3` metadata and Apache-2.0 licensing. The API reports 8,190,735,360 BF16 parameters, five safetensor weight shards, warm inference status, 13,657,580 downloads, 1,330 likes, and 45,450,222,438 bytes of used storage.

## Analysis

The reported parameter count is approximately **8.191 billion parameters**. The reported storage corresponds to approximately **42.33 GiB**. The combination of public non-gated access, Transformers metadata, Safetensors weights, and Apache-2.0 license metadata provides concrete distribution/portability indicators suitable for observation in the SV-DN-1 problem space.

The platform counters imply approximately **10,268.86 downloads per like**, but that ratio is descriptive only. Downloads and likes are not quality, safety, capability, or governance measures.

## What this establishes

This establishes that StegVerse can retrieve current public Hugging Face source metadata and publish a transparent analysis of that source. It does **not** establish an SV-DN-1 `SDK_ADMITTED` result, StegCore/StegGate governance disposition, Master Records custody, replay/reconstruction, certification, endorsement, or production perfection.

## Governed first-round boundary

`governed_first_round_state: WITHHELD`

The canonical first production round remains separate and must replace the main SV-DN-1 dashboard only after its authentic evidence satisfies the existing fail-closed promotion predicates.
