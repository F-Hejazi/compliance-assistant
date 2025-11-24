def check_escalation(intent: str, docs: list[dict]) -> bool:
    # Example: escalate if no documents found
    return not bool(docs)
