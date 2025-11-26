import os
import requests
from dotenv import load_dotenv

load_dotenv()

AGENT_ENDPOINT = os.getenv("FOUNDRY_AGENT_ENDPOINT")
AGENT_API_KEY = os.getenv("FOUNDRY_AGENT_API_KEY")

def call_foundry_agent(user_input: str):
    if not AGENT_ENDPOINT or not AGENT_API_KEY:
        return "Foundry agent is not configured. Missing endpoint or API key."

    headers = {
        "Content-Type": "application/json",
        "api-key": AGENT_API_KEY
    }

    payload = {
        "messages": [
            {"role": "user", "content": user_input}
        ]
    }

    try:
        response = requests.post(AGENT_ENDPOINT, json=payload, headers=headers, timeout=30)
    except Exception as e:
        return f"Error contacting Foundry agent: {str(e)}"

    if response.status_code != 200:
        return f"Foundry agent returned {response.status_code}: {response.text}"

    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        return "Response format from Foundry agent was not recognized."
