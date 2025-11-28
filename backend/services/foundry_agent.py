"""
Azure Foundry Agent Service
Handles communication with Azure Foundry Agent endpoint.
"""
import os
import requests
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

AGENT_ENDPOINT = os.getenv("FOUNDRY_AGENT_ENDPOINT")
AGENT_API_KEY = os.getenv("FOUNDRY_AGENT_API_KEY")


def call_foundry_agent(messages: List[Dict[str, str]]) -> str:
    """
    Call Azure Foundry Agent with conversation history.
    
    Args:
        messages: List of message dictionaries with role and content
        
    Returns:
        Agent response text
    """
    if not AGENT_ENDPOINT or not AGENT_API_KEY:
        return "Foundry agent is not configured. Please check environment variables."
    
    headers = {
        "Content-Type": "application/json",
        "api-key": AGENT_API_KEY
    }
    
    payload = {"messages": messages}
    
    try:
        response = requests.post(
            AGENT_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        data = response.json()
        return data["choices"][0]["message"]["content"]
        
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException as e:
        return f"Error contacting Foundry agent: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Unexpected response format: {str(e)}"

