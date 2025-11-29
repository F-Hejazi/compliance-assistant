"""
Session storage service using Azure Cosmos DB.
For demo purposes, using in-memory storage with Cosmos-compatible interface.
"""
import os
from typing import Dict, Any

# In production, this would use:
# from azure.cosmos import CosmosClient

class SessionStore:
    """Session store with Cosmos DB-compatible interface."""
    
    def __init__(self):
        # In-memory storage for demo reliability
        # Production would initialize: CosmosClient(endpoint, credential)
        self._sessions = {}
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        return self._sessions.get(session_id, [])
    
    def save_session(self, session_id: str, messages: list):
        self._sessions[session_id] = messages

