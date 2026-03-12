from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from doc_gate import StegVerseGate

@dataclass
class MutationReceipt:
    mutation_receipt_id:str; mutation_name:str; sequence:int; previous_mutation_receipt_id:str; current_state:str; required_state:str; decision:str; timestamp_utc:str; mutation_receipt_hash:str
    def to_dict(self): return self.__dict__.copy()

class MutationGate:
    def __init__(self, repo_root:Path):
        self.repo_root=Path(repo_root).resolve(); self.mutations_path=self.repo_root/'engine'/'mutations.json'; self.runtime_dir=self.repo_root/'.stegverse_runtime'; self.mutation_receipts_path=self.runtime_dir/'mutation_receipts.json'
        self.runtime_dir.mkdir(parents=True, exist_ok=True); self.mutations_config=json.loads(self.mutations_path.read_text(encoding='utf-8')); self.gate=StegVerseGate(self.repo_root)
        if not self.mutation_receipts_path.exists(): self.reset()
    def reset(self): self.mutation_receipts_path.write_text('[]', encoding='utf-8')
    def _load_mutation_receipts(self): return json.loads(self.mutation_receipts_path.read_text(encoding='utf-8'))
    def _save_mutation_receipts(self, receipts): self.mutation_receipts_path.write_text(json.dumps(receipts, indent=2), encoding='utf-8')
    def mutation_receipt_chain(self): return self._load_mutation_receipts()
    def list_mutations(self): return [{'mutation':n,'required_state':cfg['required_state'],'description':cfg['description']} for n,cfg in sorted(self.mutations_config['mutations'].items())]
    def request_mutation(self, mutation_name):
        if mutation_name not in self.mutations_config['mutations']: raise KeyError(f'Unknown mutation: {mutation_name}')
        cfg=self.mutations_config['mutations'][mutation_name]; runtime=self.gate.describe_runtime(); current_state=runtime['current_state']; required_state=cfg['required_state']; decision='allowed' if current_state==required_state else 'denied'
        receipts=self._load_mutation_receipts(); prev=receipts[-1]['mutation_receipt_id'] if receipts else 'GENESIS'; ts=datetime.now(timezone.utc).isoformat()
        material=json.dumps({'mutation_name':mutation_name,'sequence':len(receipts)+1,'previous_mutation_receipt_id':prev,'current_state':current_state,'required_state':required_state,'decision':decision,'timestamp_utc':ts}, sort_keys=True).encode('utf-8')
        digest=hashlib.sha256(material).hexdigest(); rid=digest[:16].upper(); receipt=MutationReceipt(rid,mutation_name,len(receipts)+1,prev,current_state,required_state,decision,ts,digest)
        receipts.append(receipt.to_dict()); self._save_mutation_receipts(receipts)
        causal='Causal release granted: runtime state and receipt continuity permit external mutation.' if decision=='allowed' else 'Causal release withheld: system history has not yet reached an admissible mutation state.'
        return {'mutation':mutation_name,'required_state':required_state,'current_state':current_state,'decision':decision,'description':cfg['description'],'receipt':receipt.to_dict(),'message':(f'Mutation allowed: {mutation_name}\nMutation receipt generated.\n{causal}' if decision=='allowed' else f'Mutation denied: current state {current_state} does not satisfy required state {required_state}.\n{causal}')}
