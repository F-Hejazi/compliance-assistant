"""
Explainer Agent - Reasoning Generation
Generates human-readable explanations with citations.
"""
import os
from typing import Dict, Any, List
from openai import AzureOpenAI


def explain_steps(intent: str, documents: List[Dict], validation: Dict, escalation: Dict) -> str:
    """
    Generate explanation of reasoning process with citations.
    
    Args:
        intent: User's classified intent
        documents: Retrieved documents
        validation: Validation results
        escalation: Escalation decision
        
    Returns:
        Human-readable explanation with citations
    """
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # Build context from documents
        context_parts = []
        for doc in documents[:3]:  # Top 3 documents
            context_parts.append(f"[{doc.get('source', 'Unknown')}]: {doc.get('content', '')[:500]}")
        
        context = "\n\n".join(context_parts)
        
        system_prompt = f"""You are an explainer agent for immigration compliance.
Generate a clear, structured explanation based on the following:

Intent: {intent}
Documents: {context}
Validation: {validation}
Escalation: {escalation}

Provide:
1. Direct answer to the query
2. Relevant regulations/policies (cite sources)
3. Step-by-step reasoning
4. Any warnings or caveats
5. Next steps for the user

Format with clear headers and bullet points.
"""
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=[{"role": "system", "content": system_prompt}],
            temperature=0.4,
            max_tokens=800
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return _fallback_explanation(intent, documents, escalation)


def _fallback_explanation(intent: str, documents: List[Dict], escalation: Dict) -> str:
    """Generate fallback explanation when OpenAI is unavailable."""
    if escalation.get("should_escalate"):
        return f"""⚠️ This query requires human review.

**Case ID:** {escalation.get('case_id')}
**Reason:** {escalation.get('reasoning')}

An International Student Office advisor will review your case within 24 hours.
"""
    
    doc_titles = [doc.get('title', 'Document') for doc in documents[:3]]
    return f"""Based on intent: {intent}

**Relevant Information:**
- {', '.join(doc_titles)}

**Recommendation:** Please refer to the above resources or contact your International Student Office for specific guidance.
"""

