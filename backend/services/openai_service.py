"""
Azure OpenAI Service
Direct Azure OpenAI integration for classification and reasoning.
"""
import os
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()


def get_openai_client() -> AzureOpenAI:
    """Get configured Azure OpenAI client."""
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )


def classify_intent_with_openai(query: str) -> dict:
    """
    Classify user intent using Azure OpenAI.
    Wrapper function for backwards compatibility.
    """
    from backend.agents.classifier import classify_intent
    return classify_intent(query)

