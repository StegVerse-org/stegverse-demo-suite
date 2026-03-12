from __future__ import annotations
import hashlib, json
from pathlib import Path
from doc_gate import StegVerseGate
from actions.action_gate import ActionGate
from mutation_gate import MutationGate

class VerifyGate:
    def __init__(self, repo_root:Path):
        self.repo_root=Path(repo_root).resolve(); self.gate=StegVerseGate(self.repo_root); self.action_gate=ActionGate(self.repo_root); self.mutation_gate=MutationGate(self.repo_root); self.workflow=self.gate.workflow
    def _verify_workflow_chain(self):
        errors=[]; receipts=self.gate.receipt_chain(); prev='GENESIS'
        for idx,r in enumerate(receipts, start=1):
            if r['sequence']!=idx: errors.append(f"Workflow receipt sequence mismatch at {r['step_id']}.")
            if r['previous_receipt_id']!=prev: errors.append(f"Workflow receipt previous link mismatch at {r['step_id']}.")
            step=self.workflow['steps'].get(r['step_id'])
            if step is None: errors.append(f"Unknown workflow step in receipt chain: {r['step_id']}.")
            else:
                if r['state_before']!=step['from_state'] or r['state_after']!=step['to_state']: errors.append(f"Workflow state transition mismatch at {r['step_id']}.")
                if r['unlocked_document']!=step['unlocks_document']: errors.append(f"Unlocked document mismatch at {r['step_id']}.")
                material=json.dumps({'step_id':r['step_id'],'sequence':r['sequence'],'previous_receipt_id':r['previous_receipt_id'],'state_before':r['state_before'],'state_after':r['state_after'],'unlocked_document':r['unlocked_document'],'timestamp_utc':r['timestamp_utc']}, sort_keys=True).encode('utf-8')
                digest=hashlib.sha256(material).hexdigest()
                if digest!=r['receipt_hash']: errors.append(f"Workflow receipt hash mismatch at {r['step_id']}.")
                if digest[:16].upper()!=r['receipt_id']: errors.append(f"Workflow receipt id mismatch at {r['step_id']}.")
            prev=r['receipt_id']
        return len(errors)==0, errors
    def _verify_action_chain(self):
        errors=[]; receipts=self.action_gate.action_receipt_chain(); prev='GENESIS'; cfgs=self.action_gate.actions_config['actions']
        for idx,r in enumerate(receipts, start=1):
            if r['sequence']!=idx: errors.append(f"Action receipt sequence mismatch at {r['action_name']}.")
            if r['previous_action_receipt_id']!=prev: errors.append(f"Action receipt previous link mismatch at {r['action_name']}.")
            if r['action_name'] not in cfgs: errors.append(f"Unknown action in receipt chain: {r['action_name']}.")
            else:
                required=cfgs[r['action_name']]['required_state']
                if r['required_state']!=required: errors.append(f"Required state mismatch for action {r['action_name']}.")
                expected='allowed' if r['current_state']==required else 'denied'
                if r['decision']!=expected: errors.append(f"Decision mismatch for action {r['action_name']}.")
            prev=r['action_receipt_id']
        return len(errors)==0, errors
    def _verify_mutation_chain(self):
        errors=[]; receipts=self.mutation_gate.mutation_receipt_chain(); prev='GENESIS'; cfgs=self.mutation_gate.mutations_config['mutations']
        for idx,r in enumerate(receipts, start=1):
            if r['sequence']!=idx: errors.append(f"Mutation receipt sequence mismatch at {r['mutation_name']}.")
            if r['previous_mutation_receipt_id']!=prev: errors.append(f"Mutation receipt previous link mismatch at {r['mutation_name']}.")
            if r['mutation_name'] not in cfgs: errors.append(f"Unknown mutation in receipt chain: {r['mutation_name']}.")
            else:
                required=cfgs[r['mutation_name']]['required_state']
                if r['required_state']!=required: errors.append(f"Required state mismatch for mutation {r['mutation_name']}.")
                expected='allowed' if r['current_state']==required else 'denied'
                if r['decision']!=expected: errors.append(f"Decision mismatch for mutation {r['mutation_name']}.")
            prev=r['mutation_receipt_id']
        return len(errors)==0, errors
    def _verify_state_and_artifacts(self):
        errors=[]; runtime=self.gate.describe_runtime(); completed=runtime['completed_steps']
        if len(self.gate.receipt_chain())!=len(completed): errors.append('Workflow receipt count does not match completed step count.')
        expected_docs=self.gate._compute_unlocked_documents(completed)
        if runtime['unlocked_documents']!=expected_docs: errors.append('Unlocked artifact set does not match completed step history.')
        expected_state=self.workflow['steps'][completed[-1]]['to_state'] if completed else self.workflow['initial_state']
        if runtime['current_state']!=expected_state: errors.append('Current state does not match completed step history.')
        if self.gate.bulk_retrieval_allowed()!=(len(expected_docs)==len(self.workflow['documents'])): errors.append('Bulk retrieval admissibility does not match runtime state.')
        return len(errors)==0, errors
    def verify_all(self):
        wok,we=self._verify_workflow_chain(); aok,ae=self._verify_action_chain(); mok,me=self._verify_mutation_chain(); sok,se=self._verify_state_and_artifacts()
        return {'passed':wok and aok and mok and sok,'workflow_chain_verified':wok,'action_chain_verified':aok,'mutation_chain_verified':mok,'state_and_artifacts_verified':sok,'errors':we+ae+me+se,'workflow_receipts':len(self.gate.receipt_chain()),'action_receipts':len(self.action_gate.action_receipt_chain()),'mutation_receipts':len(self.mutation_gate.mutation_receipt_chain())}
