"""
Safety Agent - Content Moderation
Ensures responses are safe, unbiased, and appropriate.
"""
from typing import Dict, Any


def run_safety_check(content: str) -> Dict[str, Any]:
    """
    Run safety and content moderation checks.
    
    Args:
        content: Generated response content
        
    Returns:
        Safety check results with filtered content
    """
    safety_issues = []
    
    # Check for prohibited content patterns
    prohibited_patterns = [
        "guaranteed approval",
        "100% success",
        "always approved",
        "never denied"
    ]
    
    content_lower = content.lower()
    for pattern in prohibited_patterns:
        if pattern in content_lower:
            safety_issues.append(f"Overconfident claim detected: '{pattern}'")
    
    # Check for bias indicators
    bias_patterns = ["should be", "must be", "obviously", "clearly wrong"]
    for pattern in bias_patterns:
        if pattern in content_lower:
            safety_issues.append(f"Potential bias: '{pattern}'")
    
    # Check for PII patterns (simplified)
    import re
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    if re.search(ssn_pattern, content):
        safety_issues.append("Potential SSN detected - redacting")
        content = re.sub(ssn_pattern, "[REDACTED]", content)
    
    is_safe = len(safety_issues) == 0
    
    return {
        "is_safe": is_safe,
        "content": content,
        "safety_issues": safety_issues,
        "moderation_applied": len(safety_issues) > 0
    }

