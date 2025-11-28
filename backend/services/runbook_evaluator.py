"""
Runbook Service - Safe Automation
Evaluates rules and executes safe, predefined actions.
"""
import json
from typing import Dict, Any, List


def evaluate_rules(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate runbook rules based on context.
    
    Args:
        context: Dictionary with intent, docs, and other contextual data
        
    Returns:
        Runbook evaluation results with actions to take
    """
    intent = context.get("intent", "")
    docs = context.get("docs", [])
    
    # Define runbook rules
    rules = [
        {
            "name": "Send confirmation email",
            "condition": lambda ctx: ctx.get("intent") == "eligibility_question" and len(ctx.get("docs", [])) > 0,
            "action": "email_confirmation",
            "priority": "low"
        },
        {
            "name": "Create support ticket",
            "condition": lambda ctx: ctx.get("intent") == "escalation_needed",
            "action": "create_ticket",
            "priority": "high"
        },
        {
            "name": "Log query for analytics",
            "condition": lambda ctx: True,  # Always log
            "action": "log_query",
            "priority": "low"
        }
    ]
    
    triggered_rules = []
    for rule in rules:
        try:
            if rule["condition"](context):
                triggered_rules.append({
                    "name": rule["name"],
                    "action": rule["action"],
                    "priority": rule["priority"]
                })
        except Exception as e:
            print(f"Rule evaluation error: {e}")
    
    return {
        "triggered_rules": triggered_rules,
        "actions_taken": [r["action"] for r in triggered_rules],
        "rule_count": len(triggered_rules)
    }

    