from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
from pprint import pformat
ENGINE_DIR=Path(__file__).resolve().parent; REPO_ROOT=ENGINE_DIR.parent
if str(ENGINE_DIR) not in sys.path: sys.path.insert(0, str(ENGINE_DIR))
from doc_gate import StegVerseGate
from actions.action_gate import ActionGate
from verify_gate import VerifyGate

def build_parser():
    parser=argparse.ArgumentParser(description='StegVerse governed artifact and action workflow CLI'); sub=parser.add_subparsers(dest='command', required=True)
    for cmd in ('help','status','list','tree','bulk','receipts','action-receipts','actions','reset','demo','explain','verify'): sub.add_parser(cmd)
    run=sub.add_parser('run'); run.add_argument('step_id')
    get_doc=sub.add_parser('get'); get_doc.add_argument('document')
    act=sub.add_parser('action'); act.add_argument('action_name')
    return parser

def print_help_screen():
    print('StegVerse Runtime'); print('-'*40)
    print('Artifact commands: help, explain, status, list, tree, run <step_id>, get <document>, receipts, bulk')
    print('Action commands: actions, action <action_name>, action-receipts')
    print('Audit commands: verify')
    print('Lifecycle commands: reset, demo')

def explain_runtime(gate, action_gate):
    s=gate.describe_runtime()
    print('\nStegVerse Runtime'); print('-'*40)
    print(f"current state: {s['current_state']}"); print('completed steps:', ' '.join(s['completed_steps']) if s['completed_steps'] else 'none')
    print(f"workflow receipts: {s['total_receipts']}"); print(f"action receipts: {len(action_gate.action_receipt_chain())}")
    print('\nnext admissible steps:'); print('\n'.join([f' - {x}' for x in s['next_admissible_steps']]) if s['next_admissible_steps'] else ' - none')
    print('\ngoverned actions:'); [print(f" - {row['action']} (requires {row['required_state']})") for row in action_gate.list_actions()]
    print('\nunlocked artifacts:'); print('\n'.join([f' - {x}' for x in s['unlocked_documents']]) if s['unlocked_documents'] else ' - none')
    print('\nlocked artifacts:'); print('\n'.join([f' - {x}' for x in s['locked_documents']]) if s['locked_documents'] else ' - none')
    print('\nTip: run ./stegverse verify to audit receipt chains and runtime consistency.')

def print_tree(gate, action_gate):
    s=gate.describe_runtime(); print('StegVerse'); print('|-- state:', s['current_state']); print('|-- workflow_receipts:', s['total_receipts']); print('|-- action_receipts:', len(action_gate.action_receipt_chain()))
    print('|-- completed_steps')
    [print('|   |--', x) for x in s['completed_steps']] if s['completed_steps'] else print('|   `-- none')
    print('|-- next_admissible_steps')
    [print('|   |--', x) for x in s['next_admissible_steps']] if s['next_admissible_steps'] else print('|   `-- none')
    print('|-- governed_actions'); [print(f"|   |-- {row['action']} (requires {row['required_state']})") for row in action_gate.list_actions()]
    print('`-- artifacts')
    docs=gate.list_documents()
    for i,item in enumerate(docs):
        branch='|--' if i < len(docs)-1 else '`--'; state='UNLOCKED' if item['unlocked'] else 'LOCKED'; print(f"    {branch} {item['document']} [{state}]")
def print_verify_report(report):
    print('Verifying StegVerse runtime...')
    print('Workflow receipt chain verified.' if report['workflow_chain_verified'] else 'Workflow receipt chain FAILED.')
    print('Action receipt chain verified.' if report['action_chain_verified'] else 'Action receipt chain FAILED.')
    print('State and artifact consistency verified.' if report['state_and_artifacts_verified'] else 'State and artifact consistency FAILED.')
    if report['passed']:
        print('Runtime verification PASSED.'); print(f"Workflow receipts: {report['workflow_receipts']}"); print(f"Action receipts: {report['action_receipts']}")
    else:
        print('Runtime verification FAILED.'); [print(f'- {e}') for e in report['errors']]
def main():
    args=build_parser().parse_args(); gate=StegVerseGate(REPO_ROOT); action_gate=ActionGate(REPO_ROOT); verify_gate=VerifyGate(REPO_ROOT)
    if args.command=='help': print_help_screen(); return
    if args.command=='status': print(pformat(gate.status(), sort_dicts=False)); return
    if args.command=='list': [print(f"{'UNLOCKED' if x['unlocked'] else 'LOCKED':8} {x['document']}  ({x['path']})") for x in gate.list_documents()]; return
    if args.command=='tree': print_tree(gate, action_gate); return
    if args.command=='bulk':
        try:
            artifacts=gate.bulk_retrieval(); print(f"Retrieved {len(artifacts)} documents."); [print(f'- {x}') for x in sorted(artifacts)]
        except Exception as exc: print(exc)
        return
    if args.command=='receipts':
        rec=gate.receipt_chain()
        if not rec: print('No workflow receipts yet.'); return
        [print(f"{r['sequence']}. {r['step_id']} | {r['receipt_id']} | prev={r['previous_receipt_id']}") for r in rec]; return
    if args.command=='action-receipts':
        rec=action_gate.action_receipt_chain()
        if not rec: print('No action receipts yet.'); return
        [print(f"{r['sequence']}. {r['action_name']} | {r['action_receipt_id']} | prev={r['previous_action_receipt_id']} | decision={r['decision']}") for r in rec]; return
    if args.command=='actions': [print(f"{row['action']:15} requires={row['required_state']}  {row['description']}") for row in action_gate.list_actions()]; return
    if args.command=='reset': gate.reset(); action_gate.reset(); print('Runtime reset complete.'); return
    if args.command=='run':
        try: print(pformat(gate.run_step(args.step_id), sort_dicts=False))
        except Exception as exc: print(f'Run failed: {exc}')
        return
    if args.command=='get':
        try: print(gate.retrieve_document(args.document))
        except Exception as exc: print(f'Retrieval failed: {exc}')
        return
    if args.command=='action':
        try:
            result=action_gate.request_action(args.action_name); print(result['message']); print(pformat({'receipt_id':result['receipt']['action_receipt_id'],'decision':result['decision']}, sort_dicts=False))
        except Exception as exc: print(f'Action request failed: {exc}')
        return
    if args.command=='explain': explain_runtime(gate, action_gate); return
    if args.command=='verify': print_verify_report(verify_gate.verify_all()); return
    if args.command=='demo':
        result=subprocess.run([sys.executable, str(REPO_ROOT/'engine'/'run_demo.py')], cwd=str(REPO_ROOT), check=False); raise SystemExit(result.returncode)
if __name__=='__main__': main()
