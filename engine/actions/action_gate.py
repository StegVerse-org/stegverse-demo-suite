from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import hashlib, json
from doc_gate import StegVerseGate

@dataclass
class ActionReceipt:
    action_receipt_id:str; action_name:str; sequence:int; previous_action_receipt_id:str; current_state:str; required_state:str; decision:str; timestamp_utc:str; action_receipt_hash:str
    def to_dict(self): return self.__dict__.copy()

class ActionGate:
    def __init__(self, repo_root:Path):
        self.repo_root=Path(repo_root).resolve(); self.actions_path=self.repo_root/'engine'/'actions'/'actions.json'; self.runtime_dir=self.repo_root/'.stegverse_runtime'; self.action_receipts_path=self.runtime_dir/'action_receipts.json'
        self.runtime_dir.mkdir(parents=True, exist_ok=True); self.actions_config=json.loads(self.actions_path.read_text(encoding='utf-8')); self.gate=StegVerseGate(self.repo_root)
        if not self.action_receipts_path.exists(): self.reset()
    def reset(self): self.action_receipts_path.write_text('[]', encoding='utf-8')
    def _load_action_receipts(self): return json.loads(self.action_receipts_path.read_text(encoding='utf-8'))
    def _save_action_receipts(self, receipts): self.action_receipts_path.write_text(json.dumps(receipts, indent=2), encoding='utf-8')
    def action_receipt_chain(self): return self._load_action_receipts()
    def list_actions(self): return [{'action':n,'required_state':cfg['required_state'],'description':cfg['description']} for n,cfg in sorted(self.actions_config['actions'].items())]
    def request_action(self, action_name):
        if action_name not in self.actions_config['actions']: raise KeyError(f'Unknown action: {action_name}')
        cfg=self.actions_config['actions'][action_name]; runtime=self.gate.describe_runtime(); current_state=runtime['current_state']; required_state=cfg['required_state']; decision='allowed' if current_state==required_state else 'denied'
        receipts=self._load_action_receipts(); prev=receipts[-1]['action_receipt_id'] if receipts else 'GENESIS'; ts=datetime.now(timezone.utc).isoformat()
        material=json.dumps({'action_name':action_name,'sequence':len(receipts)+1,'previous_action_receipt_id':prev,'current_state':current_state,'required_state':required_state,'decision':decision,'timestamp_utc':ts}, sort_keys=True).encode('utf-8')
        digest=hashlib.sha256(material).hexdigest(); rid=digest[:16].upper(); receipt=ActionReceipt(rid,action_name,len(receipts)+1,prev,current_state,required_state,decision,ts,digest)
        receipts.append(receipt.to_dict()); self._save_action_receipts(receipts)
        causal='Causal release granted: admissible state and receipt continuity permit external effect.' if decision=='allowed' else 'Causal release withheld: system history has not yet reached an admissible state.'
        return {'action':action_name,'required_state':required_state,'current_state':current_state,'decision':decision,'description':cfg['description'],'receipt':receipt.to_dict(),'message':(f'Action allowed: {action_name}\nAction receipt generated.\n{causal}' if decision=='allowed' else f'Action denied: current state {current_state} does not satisfy required state {required_state}.\n{causal}')}
