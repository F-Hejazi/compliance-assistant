import os
import requests
from dotenv import load_dotenv

load_dotenv()

AGENT_ENDPOINT = os.getenv("FOUNDRY_AGENT_ENDPOINT")
AGENT_API_KEY = os.getenv("FOUNDRY_AGENT_API_KEY")

def call_foundry_agent(messages: list):
    if not AGENT_ENDPOINT or not AGENT_API_KEY:
        return "Foundry agent is not configured. Missing endpoint or API key."

    headers = {
        "Content-Type": "application/json",
        "api-key": AGENT_API_KEY
    }

    payload = {"messages": messages}  # Full conversation so far

    try:
        response = requests.post(AGENT_ENDPOINT, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error contacting Foundry agent: {str(e)}"
