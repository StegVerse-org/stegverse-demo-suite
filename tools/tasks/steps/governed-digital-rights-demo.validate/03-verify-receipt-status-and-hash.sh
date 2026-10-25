python - <<'PY'
import hashlib
import json
from pathlib import Path

path = Path('build/governed-digital-rights/receipt.json')
receipt = json.loads(path.read_text(encoding='utf-8'))
assert receipt['status'] == 'COMPLETE', receipt
recorded_hash = receipt.pop('receipt_sha256')
encoded = json.dumps(receipt, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
calculated_hash = hashlib.sha256(encoded).hexdigest()
assert recorded_hash == calculated_hash, (recorded_hash, calculated_hash)
print(json.dumps({'status': 'COMPLETE', 'receipt_sha256': recorded_hash}, sort_keys=True))
PY
