from services.search_service import search_utterances

def retrieve_documents(intent: str) -> list[dict]:
    return search_utterances(intent)
