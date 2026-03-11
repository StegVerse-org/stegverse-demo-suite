import json
from pathlib import Path

STATE_FILE = Path("workflow/state.json")
ACTIONS_FILE = Path("engine/actions/actions.json")

def load_state():
    if not STATE_FILE.exists():
        return {"state": "state0"}
    return json.loads(STATE_FILE.read_text())

def load_actions():
    return json.loads(ACTIONS_FILE.read_text())

def request_action(action_name):
    state = load_state()
    actions = load_actions()

    if action_name not in actions["allowed_actions"]:
        print(f"Action denied: {action_name} is not recognized.")
        return

    if state["state"] != "state4":
        print("Action denied: system not in admissible state.")
        return

    print(f"Action allowed: {action_name}")
    print("Execution receipt generated.")
