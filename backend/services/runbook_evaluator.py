import json
import os
from typing import Dict, Any, List

RUNBOOK_PATH = os.environ.get("RUNBOOK_PATH", "data/runbook.jsonlines")

def load_runbook() -> List[Dict[str, Any]]:
    rules = []
    try:
        with open(RUNBOOK_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rules.append(json.loads(line))
    except FileNotFoundError:
        rules = []
    return rules

# ⚠️ For demo only: replace eval with a safe evaluator in production
def rule_matches(condition: str, context: Dict[str, Any]) -> bool:
    # normalize booleans and names: caller should provide proper types
    try:
        return bool(eval(condition, {}, context))
    except Exception:
        return False

def evaluate_rules(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns a dict: { action: str, rule_id: str|null, matched_rule: dict|null }
    """
    rules = load_runbook()
    for rule in rules:
        cond = rule.get("condition", "")
        if cond and rule_matches(cond, context):
            return {
                "action": rule.get("action"),
                "rule_id": rule.get("id"),
                "rule": rule
            }
    return {"action": "manual_review", "rule_id": None, "rule": None}
