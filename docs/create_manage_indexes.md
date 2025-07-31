# How to Index Fields for Vector Search in MongoDB

MongoDB's Atlas Vector Search enables you to perform semantic searches on your data by indexing vector embeddings. You can use the `vectorSearch` type to index fields that contain vector data, along with additional fields for pre-filtering your results.

## Creating Vector Search Indexes

You can create Atlas Vector Search indexes using several methods: the Atlas UI, Atlas Administration API, Atlas CLI, `mongosh`, or supported MongoDB drivers. The index definition requires at least one vector-type field and can include additional filter fields.

Here's how to define a basic vector search index:

```python
# Python example using PyMongo
from pymongo.operations import SearchIndexModel

# Basic vector index definition
index_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "plot_embedding",
                "numDimensions": 1536,
                "similarity": "dotProduct"
            }
        ]
    },
    name="vector_index",
    type="vectorSearch"
)

# Create the index
result = collection.create_search_index(model=index_model)
print(f"Created index: {result}")
```

## Understanding Index Fields

Your vector search index definition contains several key components:

### Vector Type Fields
Vector fields must contain numeric arrays representing vector embeddings. You can specify different data types:
- BSON `double`
- Binary `BinData` with subtype `float32`, `int1`, or `int8`
- Arrays of floats

```javascript
// MongoDB Shell example
db.embedded_movies.createSearchIndex(
  "vector_index",
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
);
```

### Filter Type Fields
You can add filter fields to narrow down your search results before performing vector similarity calculations:

```python
# Python example with filter fields
index_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "plot_embedding",
                "numDimensions": 1536,
                "similarity": "dotProduct"
            },
            {
                "type": "filter",
                "path": "genres"
            },
            {
                "type": "filter",
                "path": "year"
            }
        ]
    },
    name="vector_index",
    type="vectorSearch"
)
```

## Similarity Functions

MongoDB supports three similarity functions for vector searches:

1. **euclidean** - Measures distance between vectors
2. **cosine** - Measures similarity based on angle between vectors
3. **dotProduct** - Measures similarity like cosine but considers vector magnitude

```python
# Example using different similarity functions
index_definition = {
    "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 512,
            "similarity": "cosine"  # or "euclidean", "dotProduct"
        }
    ]
}
```

## Pre-filtering Data

Pre-filtering helps optimize query performance by reducing the number of vectors that need to be compared. You can filter on various data types:

```python
# Java example with filter fields
import com.mongodb.client.model.SearchIndexModel;
import org.bson.Document;

Bson definition = new Document(
    "fields",
    Arrays.asList(
        new Document("type", "vector")
            .append("path", "plot_embedding")
            .append("numDimensions", 1536)
            .append("similarity", "dotProduct"),
        new Document("type", "filter")
            .append("path", "genres"),
        new Document("type", "filter")
            .append("path", "year")
    )
);
```

## Index Considerations

### Data Types and Dimensions
- Vector dimensions must be less than or equal to 8192
- Different data types (float32, int1, int8) have specific requirements
- For automatic quantization, use `scalar` or `binary` options

### Performance Optimization
The HNSW (Hierarchical Navigable Small Worlds) graph parameters can be tuned for better performance:

```python
# Example with HNSW options
index_definition = {
    "fields": [
        {
            "type": "vector",
            "path": "embedding",
            "numDimensions": 1536,
            "similarity": "dotProduct",
            "hnswOptions": {
                "maxEdges": 20,  # Higher values improve recall
                "numEdgeCandidates": 200  # Higher values improve quality
            }
        }
    ]
}
```

## Supported Clients

You can create and manage Atlas Vector Search indexes through multiple clients:

- **Atlas UI**: Web-based interface
- **mongosh**: Command-line shell
- **Atlas CLI**: Command-line interface
- **Atlas Administration API**: REST API
- **MongoDB Drivers**: Multiple language drivers

## View Existing Indexes

```python
# Python example to view indexes
cursor = collection.list_search_indexes()
for index in cursor:
    print(f"Index: {index['name']}")
    print(f"Type: {index['type']}")
    print(f"Status: {index['status']}")
```

## Edit Existing Indexes

You can modify existing vector search indexes without renaming or changing types:

```python
# Python example to update an index
definition = {
    "fields": [
        {
            "type": "vector",
            "path": "plot_embedding",
            "numDimensions": 1536,
            "similarity": "dotProduct",
            "quantization": "scalar"
        },
        {
            "type": "filter",
            "path": "genres"
        }
    ]
}

# Update the existing index
collection.update_search_index("vector_index", definition)
```

## Delete Indexes

```python
# Python example to delete an index
collection.drop_search_index("vector_index")
```

## Index Status Management

Indexes go through several states during creation and updates:

1. **Not Started**: Index creation has not begun
2. **Initial Sync**: Index is being built
3. **Active**: Index is ready for queries
4. **Recovering**: Replication issues occurred
5. **Failed**: Index creation failed
6. **Delete in Progress**: Index is being removed

## Best Practices

1. **Choose the right similarity function** based on your embedding model
2. **Use pre-filtering** to improve performance
3. **Consider quantization** for memory optimization
4. **Monitor index status** during building process
5. **Plan for index maintenance** as your data grows

```python
# Complete example combining all concepts
from pymongo.operations import SearchIndexModel

# Create a comprehensive vector search index
index_model = SearchIndexModel(
    definition={
        "fields": [
            {
                "type": "vector",
                "path": "plot_embedding",
                "numDimensions": 1536,
                "similarity": "dotProduct",
                "quantization": "scalar"
            },
            {
                "type": "filter",
                "path": "genres"
            },
            {
                "type": "filter",
                "path": "year"
            }
        ]
    },
    name="movie_vector_index",
    type="vectorSearch"
)

# Create the index
result = collection.create_search_index(model=index_model)
print(f"Created vector search index: {result}")
```

This approach ensures efficient vector search operations while maintaining good performance through proper indexing and filtering strategies.