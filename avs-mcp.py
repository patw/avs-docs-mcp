from pymongo import MongoClient
from fastmcp import FastMCP
from dotenv import load_dotenv
import os
import sys
import requests
from bson import ObjectId

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
DB_NAME = os.getenv('DB_NAME')
CHUNK_COLLECTION = os.getenv('CHUNK_COLLECTION')
PARENT_COLLECTION = os.getenv('PARENT_COLLECTION')
VECTOR_INDEX_NAME = os.getenv('VECTOR_INDEX_NAME')
TEXT_INDEX_NAME = os.getenv('TEXT_INDEX_NAME')
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
    parents_collection = db[PARENT_COLLECTION]
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
def search_documents_vector(query: str, limit: int = 5):
    """
    Search document chunks semantically, using vector similarity.  This is the primary search method.
    
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
                'parent_id': 1,
                'metadata': 1,
                'score': {'$meta': 'vectorSearchScore'},
                '_id': 0
            }
        }
    ]
    
    results = list(chunks_collection.aggregate(pipeline))
    return results

@mcp.tool
def search_documents_lexicaly(query: str, limit: int = 1):
    """
    Search documents using lexical similarity.  Anything in quotes should be searched with this method.
    This can also help if vector search is not finding good results.
    
    Args:
        query: The search query to find relevant document chunks
        limit: Maximum number of results to return (default: 3)
    
    Returns:
        List of documents and similarity scores
    """

    # Perform text search
    pipeline = [
        {
            "$search": {
                "index": TEXT_INDEX_NAME,
                "text": {
                    "query": query,
                    "path": "original_content"
                }
        }
        },
        {
            '$limit': limit   
        },
        {
            '$project': {
                'original_content': 1,
                'file_path': 1,
                'score': { '$meta': 'searchScore'},
                '_id': 0
            }
        }
    ]
    
    results = list(parents_collection.aggregate(pipeline))
    return results

@mcp.tool
def get_parent_document(parent_id: str):
    """
    Retrieve the full parent document by its ID. This provides a more complete answer to some questions.
    
    Args:
        parent_id: The MongoDB _id of the parent document
        
    Returns:
        The complete parent document with all original content
    """

    try:
        parent = parents_collection.find_one(
            {"_id": ObjectId(parent_id)},
            {"_id": 0, "original_content": 1, "file_path": 1}
        )
        return parent
    except Exception as e:
        return {"error": f"Failed to get parent document: {str(e)}"}

if __name__ == "__main__":
    print("\n📄 Document Search Server is running!")
    print("\nExample queries you can ask:")
    print("- 'What is ANN search?'")
    print("- 'How do I filter vector search results?'")
    print("- 'Explain vector search performance considerations'")
    
    mcp.run()
