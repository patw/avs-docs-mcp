from pymongo import MongoClient
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import sys
import requests

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
CHUNK_COLLECTION = os.getenv('CHUNK_COLLECTION')
VECTOR_INDEX_NAME = os.getenv('VECTOR_INDEX_NAME')
VOYAGE_API_KEY = os.getenv('VOYAGE_API_KEY')
VOYAGE_DIMENSIONS = int(os.getenv('VOYAGE_DIMENSIONS'))

if not all([MONGO_URI, DB_NAME, CHUNK_COLLECTION, VECTOR_INDEX_NAME, VOYAGE_API_KEY]):
    print("❌ Missing required environment variables")
    sys.exit(1)

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    chunks_collection = db[CHUNK_COLLECTION]
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print(f"❌ Could not connect to MongoDB: {e}")
    sys.exit(1)

# Create the MCP server
mcp = FastMCP("Document Search")

def get_query_embedding(query):
    """Get embedding for a query string using Voyage AI"""
    url = "https://api.voyageai.com/v1/contextualizedembeddings"
    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": [[query]],
        "input_type": "query",
        "model": "voyage-context-3",
        "output_dimension": VOYAGE_DIMENSIONS
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        res_json = response.json()
        return res_json["data"][0]["data"][0]['embedding']
    else:
        print(f"❌ Embedding error: {response.text}")
        sys.exit(1)

@mcp.tool
def search_documents(query: str, limit: int = 5):
    """
    Search document chunks using vector similarity.
    
    Args:
        query: The search query to find relevant document chunks
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        List of document chunks with metadata and similarity scores
    """
    # Get embedding for the query
    query_vector = get_query_embedding(query)
    
    # Perform vector search
    pipeline = [
        {
            '$vectorSearch': {
                'index': VECTOR_INDEX_NAME,
                'path': 'embedding',
                'queryVector': query_vector,
                'numCandidates': 100,  # 20x limit for good recall
                'limit': limit
            }
        },
        {
            '$project': {
                'text': 1,
                'metadata': 1,
                'score': {'$meta': 'vectorSearchScore'},
                '_id': 0
            }
        }
    ]
    
    results = list(chunks_collection.aggregate(pipeline))
    return results

if __name__ == "__main__":
    print("\n📄 Document Search Server is running!")
    print("\nExample queries you can ask:")
    print("- 'What is ANN search?'")
    print("- 'How do I filter vector search results?'")
    print("- 'Explain vector search performance considerations'")
    
    mcp.run()
