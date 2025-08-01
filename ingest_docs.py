import os
import glob
import requests
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel
from dotenv import load_dotenv
from langchain_text_splitters import MarkdownHeaderTextSplitter
import sys

# Load environment variables
load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
VOYAGE_DIMENSIONS = os.getenv("VOYAGE_DIMENSIONS")

# Initialize MongoDB client
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
chunks_collection = db[os.getenv("CHUNK_COLLECTION")]
parents_collection = db[os.getenv("PARENT_COLLECTION")]

# Configure markdown splitting
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

def get_embeddings_per_doc(documents, output_dimensions=1024):
    """Get embeddings for document chunks from Voyage AI"""
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
    if response.status_code == 200:
        res_json = response.json()
    else:
        print("Embedding error")
        sys.exit(1)

    embeddings_per_doc = [
        [chunk["embedding"] for chunk in doc["data"]]
        for doc in res_json["data"]
    ]

    return embeddings_per_doc

def process_markdown_files(directory="docs"):
    """Process all .md files in directory and store in MongoDB"""
    md_files = glob.glob(os.path.join(directory, "**/*.md"), recursive=True)
    
    for file_path in md_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Split markdown into chunks
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on)
        splits = splitter.split_text(markdown_content)
        
        # Get text chunks and generate embeddings
        chunk_texts = [split.page_content for split in splits]
        embeddings = get_embeddings_per_doc([chunk_texts], VOYAGE_DIMENSIONS)[0]
        
        # Insert parent document
        parent_doc = {
            "file_path": file_path,
            "original_content": markdown_content,
            "chunk_ids": []
        }
        parent_result = parents_collection.insert_one(parent_doc)
        parent_id = parent_result.inserted_id
        
        # Insert chunks with embeddings and parent reference
        chunk_ids = []
        for split, embedding in zip(splits, embeddings):
            chunk_doc = {
                "text": split.page_content,
                "metadata": split.metadata,
                "embedding": embedding,
                "parent_id": parent_id
            }
            chunk_result = chunks_collection.insert_one(chunk_doc)
            chunk_ids.append(chunk_result.inserted_id)
        
        # Update parent with chunk references
        parents_collection.update_one(
            {"_id": parent_id},
            {"$set": {"chunk_ids": chunk_ids}}
        )
        
        print(f"Processed {file_path} with {len(chunk_ids)} chunks")

def create_vector_index():
    """Create a vector search index for the chunks collection"""
    index_model = SearchIndexModel(
        definition={
            "fields": [
                {
                    "type": "vector",
                    "path": "embedding",
                    "numDimensions": int(VOYAGE_DIMENSIONS), 
                    "similarity": "cosine",  # Best for semantic search
                },
                {
                    "type": "filter",
                    "path": "parent_id"  # Allow filtering by parent document
                }
            ]
        },
        name=os.getenv("VECTOR_INDEX_NAME"),
        type="vectorSearch"
    )

    # Create the index
    result = chunks_collection.create_search_index(model=index_model)
    print(f"Created vector search index: {result}")

    # Verify index was created
    indexes = list(chunks_collection.list_search_indexes())
    print(f"Current chunks indexes: {[idx['name'] for idx in indexes]}")

def create_text_index():
    """Create a text search index for the parents collection"""
    index_model = SearchIndexModel(
        definition={
            "analyzer": "lucene.english",
            "searchAnalyzer": "lucene.english",
            "mappings": {
                "dynamic": False,
                "fields": {
                    "original_content": {
                        "type": "string"
                    }
                }
            }
        },
        name=os.getenv("TEXT_INDEX_NAME")
    )

    # Create the index
    result = parents_collection.create_search_index(model=index_model)
    print(f"Created text search index: {result}")

    # Verify index was created
    indexes = list(chunks_collection.list_search_indexes())
    print(f"Current parent indexes: {[idx['name'] for idx in indexes]}")

if __name__ == "__main__":
    # Clear existing collections
    try:
        chunks_collection.drop()
        parents_collection.drop()
        print("Dropped existing collections")
    except:
        pass
    
    # Process documents and create indexes
    process_markdown_files()
    create_vector_index()
    create_text_index()
