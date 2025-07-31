import requests
import os

# Set your API key
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")  # or replace with your actual key as a string

# Send a list of documents with chunks and get a list of embeddings per document back
# output_dimensions supports 2048, 1024, 512 and 256
def get_embeddings_per_doc(documents, output_dimensions = 1024):
    url = "https://api.voyageai.com/v1/contextualizedembeddings"
    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": documents,
        "input_type": "document",
        "model": "voyage-context-3",
        "output_dimension": output_dimensions
    }

    response = requests.post(url, headers=headers, json=data)
    res_json = response.json()

    embeddings_per_doc = [
        [chunk["embedding"] for chunk in doc["data"]]
        for doc in res_json["data"]
    ]

    return embeddings_per_doc

# Send a list of documents with chunks and get a list of embeddings per document back
# output_dimensions supports 2048, 1024, 512 and 256
def get_query_embedding(query, output_dimensions = 1024):
    url = "https://api.voyageai.com/v1/contextualizedembeddings"
    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "inputs": [[query]],
        "input_type": "query",
        "model": "voyage-context-3",
        "output_dimension": output_dimensions
    }

    response = requests.post(url, headers=headers, json=data)
    res_json = response.json()

    return res_json["data"][0]["data"][0]['embedding']


# Sample document chunks
docs = [
    ["doc_1_chunk_1", "doc_1_chunk_2", "doc_1_chunk_3"],
    ["doc_2_chunk_1", "doc_2_chunk_2"]
]

# Get embeddings for docs in a nested array
print(get_embeddings_per_doc(docs, 256))

# Get single query embedding
print(get_query_embedding("Stuff", 256))

