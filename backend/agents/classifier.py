from ..services.openai_service import classify_intent_with_openai

def classify_intent(text: str) -> str:
    return classify_intent_with_openai(text)
