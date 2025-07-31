# Atlas Vector Search Overview

MongoDB Atlas provides a powerful vector database solution through **Atlas Vector Search**, which allows you to seamlessly index and query vector data alongside your traditional MongoDB documents. This capability is especially valuable for AI applications, enabling semantic search, hybrid search, and retrieval-augmented generation (RAG) workflows. By integrating vector search directly into your MongoDB cluster, you can perform complex queries that consider not just exact matches but also **semantic similarity** — meaning the meaning or intent behind your data.

Atlas Vector Search supports both **Approximate Nearest Neighbor (ANN)** and **Exact Nearest Neighbor (ENN)** algorithms, depending on your MongoDB version. For example:

- **ANN** is supported on clusters running MongoDB **v6.0.11**, **v7.0.2**, or later
- **ENN** is supported on clusters running MongoDB **v6.0.16**, **v7.0.10**, **v7.3.2**, or later

This makes it possible to balance accuracy with performance when retrieving the most relevant results for various use cases such as recommendation systems, content discovery, and intelligent agents.

---

## What is Vector Search?

Vector search works by converting your data into numerical representations called **vectors**, which capture the semantic meaning of that data in multi-dimensional space. Instead of matching keywords like traditional full-text search, vector search evaluates the **distance** between vectors to determine similarity.

For instance, searching for "red fruit" using full-text search would only return documents containing those exact words. In contrast, vector search can return documents like "apple" or "strawberry" even if they don't explicitly mention "red fruit", because their embeddings are semantically close to your query vector.

This ability to interpret intent and context makes vector search ideal for natural language understanding, image recognition, and more.

---

## Use Cases

Atlas Vector Search enables a range of real-world applications:

### Semantic Search

Perform semantic similarity searches using either **ANN** or **ENN** algorithms. For example:

```javascript
db.collection.aggregate([
  {
    $vectorSearch: {
      queryVector: [0.12, 0.34, 0.56],
      path: "embedding",
      numCandidates: 100,
      limit: 10
    }
  }
])
```

This stage finds the 10 most similar vectors in the `embedding` field of your documents.

### Hybrid Search

Combine vector search with full-text search to get richer results. You might search for articles that mention "climate change" and are semantically related to "global warming".

### Generative Search (RAG)

Use Atlas Vector Search with Retrieval-Augmented Generation (RAG) to enhance large language model responses. You can store documents and their vector representations in MongoDB, then query them during inference to provide context.

---

## AI Integrations

Atlas Vector Search integrates well with popular AI platforms and frameworks such as LangChain, LlamaIndex, and Hugging Face Transformers. These integrations allow developers to build applications quickly that leverage vector search, embeddings, and generative AI.

You can connect Atlas with embedding models like those from OpenAI, Cohere, or Voyage AI to generate vector embeddings and store them directly in MongoDB.

---

## Key Concepts

### Vectors and Embeddings

A **vector** is an array of numbers that represents your data in a multi-dimensional space. These vectors often represent textual, image, or audio content. In Atlas Vector Search, we primarily use **dense vectors**, which offer better performance and richer semantic representation than sparse vectors.

**Embedding models** convert raw data (e.g., text) into these dense vectors. Common models include BERT, Sentence Transformers, and specialized ones like those from Voyage AI.

```javascript
// Example of storing an embedding in a document
{
  "_id": ObjectId("..."),
  "title": "Climate Change and Its Effects",
  "content": "Global warming has led to rising sea levels...",
  "embedding": [0.12, 0.34, 0.56, ...]  // A vector representation of content
}
```

### Indexing and Filtering

To perform vector search, you must define an **Atlas Vector Search index**. This index tells Atlas which fields contain the vector embeddings and how to efficiently retrieve them.

```json
{
  "mappings": {
    "fields": {
      "embedding": {
        "type": "vector",
        "dimensions": 1536,
        "similarity": "cosine"
      }
    }
  }
}
```

You can also **pre-filter** your data using standard MongoDB operators to limit the dataset searched.

```javascript
db.collection.aggregate([
  {
    $match: { category: "technology" }
  },
  {
    $vectorSearch: {
      queryVector: [0.12, 0.34, 0.56],
      path: "embedding",
      numCandidates: 100,
      limit: 10
    }
  }
])
```

---

## Atlas Vector Search Indexes

An Atlas Vector Search index must be defined before performing vector queries. It specifies:

- The embedding field
- The number of dimensions
- The similarity metric (e.g., cosine, euclidean)
- Any fields to pre-filter on

Atlas supports up to **8192-dimensional** embeddings.

To create an index, you can use the MongoDB Atlas UI or the `createSearchIndex` command.

---

## Atlas Vector Search Queries

The core of a vector search query is the `$vectorSearch` aggregation stage. Here's a breakdown of how it works:

1. **Select algorithm** (ANN or ENN)
2. **Specify query vector**
3. **Choose the embedding field**
4. **Set parameters like `numCandidates` and `limit`**

Example query:

```javascript
db.collection.aggregate([
  {
    $vectorSearch: {
      queryVector: [0.12, 0.34, 0.56],
      path: "embedding",
      numCandidates: 100,
      limit: 10,
      filter: { status: "published" }
    }
  },
  {
    $project: {
      _id: 1,
      title: 1,
      score: { $meta: "vectorSearchScore" }
    }
  }
])
```

In this example, we filter results where `status` equals `"published"` and project only the title and relevance score.

---

## Next Steps

To dive deeper into working with Atlas Vector Search, consider:

- [Atlas Vector Search Quick Start](https://mongodb.com/docs/atlas/atlas-vector-search/tutorials/vector-search-quick-start/#std-label-vector-search-quick-start)
- [Atlas Vector Search Tutorials](https://mongodb.com/docs/atlas/atlas-vector-search/tutorials/#std-label-avs-tutorials)
- [MongoDB University Course: Using Vector Search for Semantic Search](https://learn.mongodb.com/courses/using-vector-search-for-semantic-search)

For optimal performance, especially under heavy query loads, we recommend configuring **dedicated search nodes** for workload isolation.

---

By leveraging Atlas Vector Search, you can easily build AI-driven applications that go beyond keyword matching, enabling semantic understanding, intelligent filtering, and robust retrieval capabilities. Whether you're developing chatbots, recommendation engines, or advanced content search systems, Atlas offers the flexibility and scalability needed to power your vector-based workflows.