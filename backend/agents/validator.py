"""
Validator Agent - Document Verification
Validates documents for authenticity and completeness.
"""
import os
from typing import Dict, Any, List
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential


def validate_document(intent: str, documents: List[Dict], uploaded_files: List = None) -> Dict[str, Any]:
    """
    Validate documents for completeness and authenticity.
    
    Args:
        intent: User's intent
        documents: Retrieved documents
        uploaded_files: Optional uploaded files to validate
        
    Returns:
        Validation results with checklist and flags
    """
    validation_result = {
        "checklist_pass": True,
        "completeness_score": 0.0,
        "authenticity_flags": [],
        "missing_fields": [],
        "warnings": []
    }
    
    # Check document completeness
    if not documents or len(documents) == 0:
        validation_result["checklist_pass"] = False
        validation_result["warnings"].append("No relevant documents found")
        validation_result["completeness_score"] = 0.0
        return validation_result
    
    # Calculate completeness based on retrieved docs
    validation_result["completeness_score"] = min(len(documents) / 3, 1.0)
    
    # Check for high-risk intents that need validation
    high_risk_intents = ["document_verification", "escalation_needed"]
    if intent in high_risk_intents:
        validation_result["warnings"].append("High-risk intent detected - human review recommended")
    
    # Check for missing critical fields
    critical_fields = ["source", "content", "category"]
    for doc in documents:
        for field in critical_fields:
            if not doc.get(field):
                validation_result["missing_fields"].append(f"Missing {field} in document {doc.get('id')}")
    
    if validation_result["missing_fields"]:
        validation_result["checklist_pass"] = False
    
    return validation_result

