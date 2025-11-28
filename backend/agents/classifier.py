"""
Classifier Agent - Intent Recognition
Analyzes user queries to determine intent and route to appropriate handlers.
"""
import os
from typing import Dict, Any
from openai import AzureOpenAI


def classify_intent(query: str) -> Dict[str, Any]:
    """
    Classify user query intent using Azure OpenAI.
    
    Args:
        query: User's input text
        
    Returns:
        Dictionary with intent classification and confidence score
    """
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2024-02-15-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        system_prompt = """You are a classification agent for immigration compliance queries.
Classify the user's intent into one of these categories:
- eligibility_question
- document_verification
- policy_interpretation
- deadline_inquiry
- escalation_needed
- general_inquiry

Respond in JSON format: {"intent": "category", "confidence": 0.0-1.0, "reasoning": "brief explanation"}
"""
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0.3,
            max_tokens=150
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            "intent": result.get("intent", "general_inquiry"),
            "confidence": result.get("confidence", 0.5),
            "reasoning": result.get("reasoning", "")
        }
        
    except Exception as e:
        # Fallback classification
        return {
            "intent": "general_inquiry",
            "confidence": 0.5,
            "reasoning": f"Classification error: {str(e)}"
        }

