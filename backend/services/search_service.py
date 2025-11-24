import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

# Load .env from the project root
load_dotenv()

endpoint = os.getenv("SEARCH_ENDPOINT")
index_name = os.getenv("SEARCH_INDEX")
api_key = os.getenv("SEARCH_API_KEY")

if not endpoint or not index_name or not api_key:
    raise RuntimeError("Missing required environment variables")

search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(api_key)
)

def search_utterances(query):
    results = search_client.search(query)
    return [doc for doc in results]
