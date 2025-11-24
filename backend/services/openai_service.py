import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

if not AZURE_OPENAI_ENDPOINT or not AZURE_OPENAI_KEY or not AZURE_OPENAI_DEPLOYMENT_NAME:
    raise RuntimeError(
        "Missing one or more Azure OpenAI environment variables: "
        "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_DEPLOYMENT_NAME"
    )

client = AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_version="2025-01-01-preview"
)

def classify_intent_with_openai(text: str) -> str:
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT_NAME or "gpt-4o",
        messages=[
            {
                "role": "user",
                "content": (
                    "Classify the intent of this user input using a single short label. "
                    "User input: " + text
                )
            }
        ],
        max_tokens=20,
        temperature=0
    )
    content = getattr(response.choices[0].message, "content", None)
    if content is None:
        return ""
    return content.strip()
