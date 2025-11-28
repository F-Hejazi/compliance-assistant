"""
Escalation Agent - Human Handoff Logic
Determines when queries require human expert intervention.
"""
from typing import Dict, Any, List


def check_escalation(intent: str, documents: List[Dict], confidence: float = 0.5) -> Dict[str, Any]:
    """
    Determine if query requires human escalation.
    
    Args:
        intent: Classified intent
        documents: Retrieved documents
        confidence: Classification confidence score
        
    Returns:
        Escalation decision with reasoning
    """
    escalation_triggers = {
        "low_confidence": confidence < 0.7,
        "no_documents": len(documents) == 0,
        "high_risk_intent": intent in ["document_verification", "escalation_needed"],
        "conflicting_information": _check_conflicts(documents),
        "missing_critical_data": not all(doc.get("content") for doc in documents)
    }
    
    should_escalate = any(escalation_triggers.values())
    
    # Generate case ID if escalating
    case_id = None
    if should_escalate:
        import uuid
        case_id = f"CLW-2024-ESC-{uuid.uuid4().hex[:6].upper()}"
    
    triggered_reasons = [k for k, v in escalation_triggers.items() if v]
    
    return {
        "should_escalate": should_escalate,
        "case_id": case_id,
        "priority": "high" if len(triggered_reasons) > 2 else "medium",
        "triggered_reasons": triggered_reasons,
        "reasoning": _generate_escalation_reasoning(triggered_reasons)
    }


def _check_conflicts(documents: List[Dict]) -> bool:
    """Check if documents contain conflicting information."""
    # Simplified conflict detection
    if len(documents) < 2:
        return False
    
    # Check for contradictory keywords
    conflicting_pairs = [("eligible", "ineligible"), ("approved", "denied"), ("yes", "no")]
    
    for doc1 in documents:
        content1 = doc1.get("content", "").lower()
        for doc2 in documents:
            if doc1 == doc2:
                continue
            content2 = doc2.get("content", "").lower()
            for term1, term2 in conflicting_pairs:
                if term1 in content1 and term2 in content2:
                    return True
    
    return False


def _generate_escalation_reasoning(reasons: List[str]) -> str:
    """Generate human-readable escalation reasoning."""
    reason_map = {
        "low_confidence": "The system has low confidence in its classification",
        "no_documents": "No relevant policy documents were found",
        "high_risk_intent": "This query involves high-stakes compliance decisions",
        "conflicting_information": "Retrieved documents contain conflicting information",
        "missing_critical_data": "Critical information is missing from available documents"
    }
    
    explanations = [reason_map.get(r, r) for r in reasons]
    return " | ".join(explanations)

