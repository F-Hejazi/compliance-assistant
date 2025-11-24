def explain_steps(intent: str, docs: list[dict], validation: dict, escalation: bool) -> str:
    return f"Intent: {intent}, Docs retrieved: {len(docs)}, Validation: {validation}, Escalation: {escalation}"
