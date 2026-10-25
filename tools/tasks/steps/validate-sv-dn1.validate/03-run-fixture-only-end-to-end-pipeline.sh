rm -rf /tmp/sv-dn1-proof
python scripts/run_sv_dn1.py \
  --input fixtures/sv_dn1/hf_model_baseline.json \
  --native-ref https://huggingface.co/stegverse-fixture/example-open-model \
  --observed-at 2026-08-27T12:00:00Z \
  --output-dir /tmp/sv-dn1-proof
