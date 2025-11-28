"""
Azure Cognitive Search Service
Handles search operations against the knowledge base.
"""
import os
from typing import List, Dict
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


def search_utterances(query: str, top_k: int = 5) -> List[Dict]:
    """
    Search for relevant documents using Azure Cognitive Search.
    
    Args:
        query: Search query
        top_k: Number of results to return
        
    Returns:
        List of search results
    """
    try:
        search_endpoint = os.getenv("SEARCH_ENDPOINT")
        search_key = os.getenv("SEARCH_API_KEY")
        index_name = os.getenv("SEARCH_INDEX", "immigration-policies")
        
        if not search_endpoint or not search_key:
            return []
        
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key)
        )
        
        results = search_client.search(
            search_text=query,
            top=top_k,
            select=["id", "title", "content", "source"]
        )
        
        return [dict(result) for result in results]
        
    except Exception as e:
        print(f"Search error: {e}")
        return []

