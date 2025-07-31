# Running Vector Search Queries in MongoDB Atlas

MongoDB Atlas Vector Search enables semantic search queries using aggregation pipeline stages. The `$vectorSearch` stage performs either Approximate Nearest Neighbor (ANN) or Exact Nearest Neighbor (ENN) searches on vector embeddings within your data.

## ANN vs ENN Search

**Approximate Nearest Neighbor (ANN)** searches use the Hierarchical Navigable Small Worlds algorithm to efficiently find similar vectors without scanning every document. This approach works best for large datasets and provides ~90-95% recall with significantly lower latency compared to exact search methods. For optimal performance, tune the `numCandidates` parameter to at least 20 times your desired `limit`.

**Exact Nearest Neighbor (ENN)** searches exhaustively calculate distances between all indexed vectors and return exact matches. While more computationally intensive, ENN is recommended for:
- Determining ANN accuracy
- Querying less than 10,000 documents
- Using selective pre-filters on collections where less than 5% of data meets criteria

## Basic Syntax

```python
pipeline = [
    {
        '$vectorSearch': {
            'index': 'vector_index',
            'path': 'plot_embedding',
            'queryVector': [-0.0016261312, -0.028070757, ...],
            'numCandidates': 150,
            'limit': 10
        }
    },
    {
        '$project': {
            '_id': 0,
            'plot': 1,
            'title': 1,
            'score': {'$meta': 'vectorSearchScore'}
        }
    }
]
```

The essential parameters include:
- `index`: Name of your Atlas Vector Search index
- `path`: Field containing vector embeddings
- `queryVector`: Array of numbers representing your search query
- `numCandidates`: Number of nearest neighbors to consider (required for ANN)
- `limit`: Maximum results to return

## Pre-filtering Data

You can improve query performance by filtering documents before vector search:

```python
pipeline = [
    {
        '$vectorSearch': {
            'index': 'vector_index',
            'path': 'plot_embedding',
            'filter': {
                '$and': [
                    {'year': {'$gt': 1955}},
                    {'year': {'$lt': 1975}}
                ]
            },
            'queryVector': [0.02421053, -0.022372592, ...],
            'numCandidates': 150,
            'limit': 10
        }
    },
    {
        '$project': {
            '_id': 0,
            'title': 1,
            'plot': 1,
            'year': 1,
            'score': {'$meta': 'vectorSearchScore'}
        }
    }
]
```

## Understanding Search Scores

Atlas Vector Search assigns scores from 0 to 1, where 1 indicates highest similarity. The scoring method depends on your index configuration:
- For cosine and dotProduct similarity, score = (1 + similarity) / 2
- For Euclidean distance, score = 1 / (1 + distance)

## Performance Considerations

For optimal ANN search performance, set `numCandidates` to at least 20 times your `limit` value. Larger datasets typically require higher `numCandidates`. Consider using dedicated Search Nodes for better parallel query execution, especially on high-CPU systems.

## Supported Clients

Atlas Vector Search works with:
- MongoDB Shell (`mongosh`)
- All MongoDB drivers
- Atlas UI
- Local Atlas deployments via Atlas CLI

## Query Limitations

- Available on MongoDB v6.0.11+, v7.0.2+
- Cannot be used in views or certain aggregation stages
- Must be the first stage in an aggregation pipeline
- Requires vector type field indexed in a vectorSearch index

These examples demonstrate how to implement semantic search queries with Atlas Vector Search across multiple programming languages, showing both basic and filtered search scenarios.