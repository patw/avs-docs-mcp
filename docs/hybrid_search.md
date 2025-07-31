# Hybrid Search with Atlas Vector Search and Atlas Search

This tutorial demonstrates how to perform a hybrid search that combines both full-text and semantic search capabilities using MongoDB Atlas. This approach leverages the strengths of both search methods to deliver more comprehensive and relevant results.

## Understanding Hybrid Search

Hybrid search combines two different search approaches:
- **Full-text search**: Excels at finding exact matches for query terms
- **Semantic search**: Identifies semantically similar documents, even without exact term matches

This combination ensures that synonymous terms and contextually related content are also included in search results, providing a richer search experience.

## Setting Up the Environment

Before beginning, you'll need:
- Access to a MongoDB Atlas cluster with Project Data Access Admin permissions
- The `sample_mflix.embedded_movies` collection containing movie data with plot embeddings

### Creating Required Indexes

First, create the necessary indexes on your collection:

```python
# Create Atlas Vector Search index on plot_embedding field
db.embedded_movies.createSearchIndex(
    "hybrid-vector-search",
    "vectorSearch",
    {
        "fields": [
            {
                "type": "vector",
                "path": "plot_embedding",
                "numDimensions": 1536,
                "similarity": "dotProduct"
            }
        ]
    }
)

# Create Atlas Search index on title field
db.embedded_movies.createSearchIndex(
    "hybrid-full-text-search",
    "search",
    {
        "mappings": {
            "dynamic": True
        }
    }
)
```

## Performing the Hybrid Search

The hybrid search uses MongoDB's aggregation pipeline with the `$rankFusion` stage to combine results from both search methods:

```python
# Example query using hybrid search
query_embedding = [-0.0031186682172119617, -0.01895737089216709, ...]  # 1536-dimensional vector

pipeline = [
    {
        "$rankFusion": {
            "input": {
                "pipelines": {
                    "vectorPipeline": [
                        {
                            "$vectorSearch": {
                                "index": "hybrid-vector-search",
                                "path": "plot_embedding",
                                "queryVector": query_embedding,
                                "numCandidates": 100,
                                "limit": 20
                            }
                        }
                    ],
                    "fullTextPipeline": [
                        {
                            "$search": {
                                "index": "hybrid-full-text-search",
                                "phrase": {
                                    "query": "star wars",
                                    "path": "title"
                                }
                            }
                        },
                        {"$limit": 20}
                    ]
                }
            },
            "combination": {
                "weights": {
                    "vectorPipeline": 0.7,
                    "fullTextPipeline": 0.3
                }
            },
            "scoreDetails": True
        }
    },
    {
        "$project": {
            "_id": 1,
            "title": 1,
            "plot": 1,
            "scoreDetails": {"$meta": "scoreDetails"}
        }
    },
    {"$limit": 20}
]

results = db.embedded_movies.aggregate(pipeline)
```

## How the Algorithm Works

The hybrid search algorithm uses **reciprocal rank fusion** to combine results:

1. Each search method ranks documents independently
2. Documents receive scores based on their position: `1.0 / (position + 60)`
3. The scores from both methods are weighted and combined
4. Final ranking considers documents that appear in both search results

For example, if a document ranks 2nd in full-text search and 1st in vector search:
- Full-text score: 1.0 / (2 + 60) = 0.0161
- Vector score: 1.0 / (1 + 60) = 0.0163
- Weighted scores with weights 0.3 and 0.7 respectively
- Combined score: (0.3 × 0.0161) + (0.7 × 0.0163) = 0.0162

## Practical Benefits

This hybrid approach offers several advantages:
- **Improved relevance**: Combines exact matching with semantic understanding
- **Flexibility**: Adjustable weights to prioritize one search method over another
- **Better coverage**: Finds both literal matches and conceptually similar content
- **Reduced false positives**: Documents appearing in both searches get higher priority

The system handles duplicate documents automatically, ensuring that movies appearing in both the semantic and full-text search results are ranked higher in the final output.

This implementation demonstrates how MongoDB's Atlas Vector Search and Atlas Search can work together to provide powerful, flexible search capabilities that exceed what either method could achieve alone.