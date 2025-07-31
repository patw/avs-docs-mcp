# Atlas Vector Search Quantization

Atlas Vector Search provides automatic quantization capabilities for your vector embeddings, supporting both 32-bit and 64-bit float vectors. Additionally, it can ingest and index pre-quantized scalar and binary vectors from certain embedding models, offering flexibility in how you store and process vector data.

## Understanding Quantization

Quantization is a process that reduces high-fidelity vectors to lower bit representations, significantly decreasing memory requirements for storing vector embeddings in Atlas Vector Search indexes. Instead of storing full precision vectors, the system indexes reduced representation vectors, allowing for storage of more vectors or vectors with higher dimensions while maintaining performance. This approach reduces resource consumption and improves query speed, making it particularly beneficial for applications handling large numbers of vectors (typically over 100,000 vectors).

### Scalar Quantization

Scalar quantization works by identifying the minimum and maximum values for each dimension in the indexed vectors to establish a range. The range is then divided into equally sized intervals or bins. Each float value is mapped to a bin, effectively converting continuous float values into discrete integers. This process reduces memory costs to approximately one fourth (1/3.75) of the original cost.

### Binary Quantization

Binary quantization assumes a midpoint of 0 for each dimension, which is appropriate for embeddings normalized to length 1, such as OpenAI's `text-embedding-3-large`. Each value in the vector is compared to this midpoint: values greater than 0 become 1, and values less than or equal to 0 become 0. This method reduces memory costs to one twenty-fourth (1/24) of the original cost. The reason it's not 1/32 is that the Hierarchical Navigable Small Worlds (HNSW) graph data structure, separate from the vector values, isn't compressed.

When running queries, Atlas Vector Search converts float query vectors into binary vectors using the same midpoint for efficient comparison. The system then re-ranks candidates using the original float values to refine results. Full-fidelity vectors are stored separately on disk and only referenced during rescoring.

## Quantization Requirements

Atlas Vector Search supports various quantization types with specific requirements:

- **Storage**: All floating-point values are stored as `double` internally, making both 32-bit and 64-bit embeddings compatible with automatic quantization
- **Supported Similarity Methods**: All quantization types support `euclidean`, `cosine`, and `dotProduct` similarity functions
- **Dimensions**: Support for 1 to 8192 dimensions across all quantization methods
- **Search Types**: Both ANN (Approximate Nearest Neighbor) and ENN (Exact Nearest Neighbor) search capabilities are available

## Enabling Automatic Quantization

You can configure Atlas Vector Search to automatically quantize float vectors by specifying a `quantization` field value of either `scalar` or `binary` in your index definition. This triggers an index rebuild and applies to all indexed and query vectors at runtime without requiring changes to your queries.

For most embedding models, binary quantization with rescoring is recommended. For lower dimension models that are not Quantization-Aware-Trained, scalar quantization is preferred due to minimal representational loss.

### Benefits of Automatic Quantization

- Reduces RAM usage by 3.75x for scalar quantization and 24x for binary quantization
- Improves overall performance at high volume and scale
- Maintains accuracy through rescoring mechanisms
- Enables efficient processing of large vector datasets

### Use Cases

Automatic quantization is particularly recommended for:
- Applications with over 100,000 full-fidelity vectors
- Scenarios where memory efficiency is critical
- Workloads requiring high-scale vector search capabilities

## Ingesting Pre-Quantized Vectors

Atlas Vector Search also supports ingestion of scalar and binary quantized vectors from embedding models using BSON BinData format. This allows you to use pre-quantized vectors directly without needing to perform quantization during indexing.

### Benefits of Pre-Quantized Vectors

- Disk space reduction of approximately 3x compared to standard float32 arrays
- Reduced memory footprint for building indexes
- Efficient storage and retrieval of quantized embeddings

### Supported Subtypes

The system supports `float32`, `int1`, and `int8` subtypes through BSON BinData vectors with various drivers including Go, Java, Node.js, and Python.

### Prerequisites

To work with pre-quantized vectors, ensure you have:
- Atlas cluster running MongoDB version 6.0.11, 7.0.2, or later
- Access to embedding models that support byte vector output
- Required drivers installed for your programming language

## Implementation Examples

### Python Implementation

```python
import pymongo
from bson.binary import Binary, BinaryVectorDtype

# Create BSON vectors from embeddings
bson_float32 = Binary.from_vector(float32_embedding, BinaryVectorDtype.FLOAT32)
bson_int8 = Binary.from_vector(int8_embedding, BinaryVectorDtype.INT8)
bson_int1 = Binary.from_vector(int1_embedding, BinaryVectorDtype.PACKED_BIT)

# Insert document with quantized vectors
document = {
    "text": "Your text data",
    "float32_vector": bson_float32,
    "int8_vector": bson_int8,
    "int1_vector": bson_int1
}
collection.insert_one(document)
```

### Node.js Implementation

```javascript
import { Binary } from 'mongodb';

// Create BSON vectors
const bsonFloat32 = Binary.fromFloat32Array(new Float32Array(float32Embedding));
const bsonInt8 = Binary.fromInt8Array(new Int8Array(int8Embedding));
const bsonInt1 = Binary.fromPackedBits(new Uint8Array(int1Embedding));

// Insert document
const document = {
    text: "Your text data",
    float32_vector: bsonFloat32,
    int8_vector: bsonInt8,
    int1_vector: bsonInt1
};
collection.insertOne(document);
```

## Evaluating Query Results

You can measure the accuracy of your vector search queries by comparing ANN (Approximate Nearest Neighbor) results with ENN (Exact Nearest Neighbor) results. This comparison helps determine how frequently ANN results include the nearest neighbors from the ENN search, providing insight into the accuracy trade-offs of quantization.

To evaluate results, you would typically:
1. Run both ANN and ENN searches for the same query
2. Compare the top-k results from each approach
3. Calculate metrics such as recall or precision to assess accuracy

This evaluation process helps you understand the impact of quantization on query accuracy and fine-tune your approach based on your specific requirements for performance versus accuracy.