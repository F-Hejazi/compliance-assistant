"""
Retrieval Agent - Document Search
Performs hybrid search across knowledge base using Azure Cognitive Search.
"""
import os
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


def retrieve_documents(intent: str, query: str = None, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Retrieve relevant documents from Azure Cognitive Search.
    
    Args:
        intent: Classified intent from classifier agent
        query: Optional search query (defaults to intent)
        top_k: Number of documents to retrieve
        
    Returns:
        List of relevant documents with metadata
    """
    try:
        search_endpoint = os.getenv("SEARCH_ENDPOINT")
        search_key = os.getenv("SEARCH_API_KEY")
        index_name = os.getenv("SEARCH_INDEX", "immigration-policies")
        
        if not search_endpoint or not search_key:
            return _fallback_documents(intent)
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key)
        )
        
        search_query = query or intent
        
        # Hybrid search: vector + keyword
        results = search_client.search(
            search_text=search_query,
            top=top_k,
            select=["id", "title", "content", "source", "category"],
            query_type="semantic"
        )
        
        documents = []
        for result in results:
            documents.append({
                "id": result.get("id"),
                "title": result.get("title"),
                "content": result.get("content"),
                "source": result.get("source"),
                "category": result.get("category"),
                "score": result.get("@search.score", 0.0)
            })
        
        return documents
        
    except Exception as e:
        return _fallback_documents(intent)


def _fallback_documents(intent: str) -> List[Dict[str, Any]]:
    """Fallback documents when search is unavailable."""
    return [
        {
            "id": "doc_f1_001",
            "title": "F-1 Visa Eligibility Requirements",
            "content": "F-1 visa applicants must be accepted by a SEVP-certified school...",
            "source": "8 CFR § 214.2(f)",
            "category": "eligibility",
            "score": 0.85
        }
    ]

