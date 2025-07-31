# Creating Vector Embeddings for MongoDB Atlas

Vector embeddings are numerical representations of data that capture semantic meaning, allowing applications to perform semantic search and implement Retrieval-Augmented Generation (RAG) with MongoDB Atlas Vector Search. These embeddings are particularly valuable for natural language processing tasks, enabling applications to understand context and relationships between different pieces of text.

## Getting Started with Vector Embeddings

To create vector embeddings in MongoDB Atlas, you first need to define a function that uses an embedding model to generate vector representations from your text data. The process involves several key steps:

1. **Define your embedding model**: Choose between open-source models like Hugging Face's `mxbai-embed-large-v1` or proprietary models like OpenAI's `text-embedding-3-small`
2. **Create embeddings from data**: Generate vector representations for your documents
3. **Store embeddings in Atlas**: Insert the embeddings into MongoDB collections
4. **Create vector search indexes**: Build Atlas Vector Search indexes for querying

Here's a basic example using Python with the `sentence-transformers` library:

```python
from sentence_transformers import SentenceTransformer

# Load an embedding model
model = SentenceTransformer("nomic-ai/nomic-embed-text-v1", trust_remote_code=True)

# Generate embeddings for text
def get_embedding(text):
    return model.encode(text, precision="float32").tolist()

# Create an embedding for a sample text
embedding = get_embedding("Titanic: The story of the 1912 sinking of the largest luxury liner ever built")
print(f"Generated embedding with {len(embedding)} dimensions")
```

## Choosing an Embedding Model

When selecting an embedding model, consider factors such as:
- **Dimensions**: Smaller embeddings are more storage-efficient but may lose nuanced relationships
- **Max Tokens**: The number of tokens that can be processed in a single embedding
- **Model Size**: Larger models perform better but require more computational resources
- **Retrieval Performance**: How well the model ranks relevant documents

For state-of-the-art embeddings, consider using Voyage AI's models, which offer superior performance for many use cases.

## Implementation Examples by Language

### Python Implementation

```python
import os
from openai import OpenAI
import pymongo

# Initialize OpenAI client
os.environ["OPENAI_API_KEY"] = "<your-api-key>"
openai_client = OpenAI()

def get_embedding(text):
    """Generate vector embeddings for given text using OpenAI"""
    embedding = openai_client.embeddings.create(
        input=[text], 
        model="text-embedding-3-small"
    ).data[0].embedding
    return embedding

# Store embeddings in MongoDB
def store_embeddings(texts, collection):
    embeddings = [get_embedding(text) for text in texts]
    
    docs = []
    for text, embedding in zip(texts, embeddings):
        docs.append({
            "text": text,
            "embedding": embedding
        })
    
    collection.insert_many(docs)
    print(f"Stored {len(docs)} documents with embeddings")

# Example usage
texts = [
    "Titanic: The story of the 1912 sinking of the largest luxury liner ever built",
    "The Lion King: Lion cub and future king Simba searches for his identity",
    "Avatar: A marine is dispatched to the moon Pandora on a unique mission"
]

# Connect to MongoDB
client = pymongo.MongoClient("<connection-string>")
db = client["sample_db"]
collection = db["embeddings"]

store_embeddings(texts, collection)
```

### Node.js Implementation

```javascript
import OpenAI from 'openai';
import { MongoClient } from 'mongodb';

// Initialize OpenAI client
const openai = new OpenAI({apiKey: process.env.OPENAI_API_KEY});

async function getEmbedding(text) {
    const results = await openai.embeddings.create({
        model: "text-embedding-3-small",
        input: text,
        encoding_format: "float",
    });
    return results.data[0].embedding;
}

async function createEmbeddings() {
    const client = new MongoClient(process.env.ATLAS_CONNECTION_STRING);
    await client.connect();
    
    const db = client.db("sample_db");
    const collection = db.collection("embeddings");
    
    const texts = [
        "Titanic: The story of the 1912 sinking of the largest luxury liner ever built",
        "The Lion King: Lion cub and future king Simba searches for his identity",
        "Avatar: A marine is dispatched to the moon Pandora on a unique mission"
    ];
    
    // Generate embeddings
    const embeddings = await Promise.all(texts.map(getEmbedding));
    
    // Insert documents with embeddings
    const documents = texts.map((text, index) => ({
        text: text,
        embedding: embeddings[index]
    }));
    
    await collection.insertMany(documents);
    console.log(`Inserted ${documents.length} documents with embeddings`);
    
    await client.close();
}
```

### Java Implementation

```java
import dev.langchain4j.data.embedding.Embedding;
import dev.langchain4j.data.segment.TextSegment;
import dev.langchain4j.model.openai.OpenAiEmbeddingModel;
import dev.langchain4j.model.output.Response;
import org.bson.BsonArray;
import org.bson.BsonDouble;

import java.util.List;
import java.util.stream.Collectors;

public class EmbeddingProvider {
    private static OpenAiEmbeddingModel embeddingModel = null;

    public static List<BsonArray> getEmbeddings(List<String> texts) {
        // Initialize embedding model
        if (embeddingModel == null) {
            embeddingModel = OpenAiEmbeddingModel.builder()
                .apiKey(System.getenv("OPEN_AI_API_KEY"))
                .modelName("text-embedding-3-small")
                .build();
        }

        List<TextSegment> textSegments = texts.stream()
            .map(TextSegment::from)
            .collect(Collectors.toList());

        Response<List<Embedding>> response = embeddingModel.embedAll(textSegments);
        return response.content().stream()
            .map(e -> new BsonArray(
                e.vectorAsList().stream()
                    .map(BsonDouble::new)
                    .collect(Collectors.toList())
            ))
            .collect(Collectors.toList());
    }
}
```

## Creating Atlas Vector Search Indexes

After storing your embeddings, you must create an Atlas Vector Search index to enable efficient querying:

```python
from pymongo.operations import SearchIndexModel

# Create search index model
search_index_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "embedding",
                "similarity": "dotProduct",
                "numDimensions": 1536  # Match your embedding model dimensions
            }
        ]
    },
    name="vector_index",
    type="vectorSearch"
)

# Create the index
collection.create_search_index(model=search_index_model)
```

## Performing Vector Searches

Once your index is created, you can perform semantic searches:

```python
# Generate query embedding
query_embedding = get_embedding("ocean tragedy")

# Execute vector search
pipeline = [
    {
        "$vectorSearch": {
            "index": "vector_index",
            "queryVector": query_embedding,
            "path": "embedding",
            "exact": True,
            "limit": 5
        }
    },
    {
        "$project": {
            "_id": 0,
            "text": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
    }
]

# Run query
results = collection.aggregate(pipeline)
for result in results:
    print(f"Text: {result['text']}")
    print(f"Score: {result['score']}")
```

## Vector Compression for Efficiency

For better storage and performance, you can compress your embeddings using BSON binary format:

```python
from bson.binary import Binary
from bson.binary import BinaryVectorDtype

def generate_bson_vector(vector, vector_dtype):
    """Convert embeddings to BSON binary format"""
    return Binary.from_vector(vector, vector_dtype)

# Example usage
bson_embedding = generate_bson_vector(embedding, BinaryVectorDtype.FLOAT32)
```

This compression reduces storage requirements by approximately 3x while maintaining query performance.

## Best Practices and Considerations

### Testing and Validation
Always test your embedding functions on small datasets before scaling to production data:

```python
# Test embedding generation
test_texts = ["Sample text 1", "Sample text 2"]
test_embeddings = [get_embedding(text) for text in test_texts]

# Verify dimensions match expected values
expected_dimensions = 1536  # For text-embedding-3-small
for i, embedding in enumerate(test_embeddings):
    assert len(embedding) == expected_dimensions, f"Embedding {i} has wrong dimensions"
```

### Performance Optimization
When working with large datasets:
1. Process embeddings in batches to manage memory usage
2. Monitor system resources during generation
3. Validate that embedding dimensions match your index specifications

### Troubleshooting
Common issues and solutions:
- **Dimension mismatches**: Ensure your embedding model dimensions match your index configuration
- **Memory issues**: Process data in smaller batches
- **Connection problems**: Verify API keys and network connectivity
- **Performance issues**: Consider vector compression and appropriate indexing strategies

## Next Steps and Advanced Features

After mastering basic embedding creation, consider implementing:
1. **Retrieval-Augmented Generation (RAG)**: Combine vector search with LLMs for enhanced applications
2. **Vector Quantization**: Further compress embeddings to reduce resource consumption
3. **Multi-modal embeddings**: Handle text, image, and other data types
4. **Advanced indexing strategies**: Optimize for your specific use cases

The ability to create and query vector embeddings in MongoDB Atlas opens up powerful semantic search capabilities that can transform how applications understand and process natural language data. By following these implementation patterns and best practices, you can build robust, scalable applications that leverage the full power of vector embeddings and Atlas Vector Search.