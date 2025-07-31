# Deployment Options for Atlas Vector Search

When deploying Atlas Vector Search for your application, choosing the right configuration is key to ensuring performance, scalability, and cost efficiency. The deployment options vary depending on whether you're in a testing/prototyping phase or moving into production.

For **testing queries**, a **Flex cluster or dedicated cluster with local deployment** is suitable. These environments support the `M0` tier or higher and allow MongoDB and Search processes to run on the same node, making them ideal for quick experimentation. For **prototyping applications**, a **dedicated cluster with `M10` or higher tiers** is recommended, as these provide better resource isolation and performance. Production-ready environments, however, require more robust configurations.

In production, it's essential to use a **dedicated cluster with separate Search Nodes**. This setup isolates the search workload from the database workload, improving performance and scalability. Search Nodes can be configured for **workload isolation** and are available in specific regions on AWS, Azure, and all regions on Google Cloud.

Each deployment type has specific **cluster tiers**, **cloud provider regions**, and **node architectures**. For example, in production, a minimum of `M10` cluster tier and `S30` search tier is recommended. Nodes must run MongoDB and Search processes on different machines to avoid resource contention, which is especially important for large datasets or high query volumes.

## Resource Usage

### Memory Requirements for Indexing Vectors

Atlas Vector Search stores entire indexes in memory, so it's crucial to allocate sufficient RAM based on your vector data size. For instance, a 1536-dimensional vector from OpenAI’s `text-embedding-ada-002` model takes 6KB of memory per vector. If you're indexing millions of such vectors, memory planning becomes critical.

With **quantization**, you can reduce memory usage significantly. For example, using **binary quantization**, memory usage can drop by up to 24x compared to full-precision vectors. When enabling automatic quantization, full-precision vectors are stored on disk, while quantized versions are in memory. The index size in memory will be much smaller than on disk, but disk space must still be allocated accordingly.

### Storage Requirements for Vectors

If you’re using **BinData** or quantized vectors, your storage needs are greatly reduced. For binary quantization, disk usage drops by 66%, and RAM usage reduces by up to 24x. For example, if you are storing 10 million 1536-dimensional vectors from OpenAI with binary quantization, the index size increases only slightly due to additional overhead (roughly 1/24th more than the original). This can be estimated using the formula:

```bash
Index size with binary quantization = Original index size * (25 / 24)
```

In practice, if your original index size is 1 GB, after binary quantization with rescoring, it would be approximately 1.042 GB.

When enabling automatic quantization, we recommend allocating **125%** of the estimated index size in disk space to allow for the full-precision vectors stored on disk.

## Testing and Prototyping Environments

For testing and prototyping, you have several options:

- **Flex Clusters or Dedicated Clusters**: Flex clusters (e.g., `M0`) are good for learning or small proof-of-concept projects. However, they may suffer from resource contention, so upgrading to `M10` or higher is recommended for more serious development.
  
- **Local Deployment**: You can also test locally using the Atlas CLI to run a single-node replica set on your machine. When ready for production, you can migrate with Live Migration.

- **Node Architecture**: In testing and prototyping, MongoDB (`mongod`) and Atlas Search (`mongot`) processes run on the same node. This simplifies setup but can lead to contention under heavy load. Performance can degrade if both services compete for resources.

For prototyping, it’s helpful to know how much memory is available for indexing. For example:

| Cluster Tier | Total Memory (GB) | Memory Available for Indexing (GB) |
|--------------|--------------------|-------------------------------------|
| `M10`        | 2                  | 1                                   |
| `M20`        | 4                  | 2                                   |
| `M30`        | 8                  | 4                                   |

### Limitations

While testing and prototyping with shared nodes is convenient, it introduces **resource contention**. Therefore, it's best suited only for non-production use cases. For production systems, it's crucial to move to **dedicated Search Nodes**.

## Production Environment

In production, a dedicated cluster with separate Search Nodes is strongly advised to ensure optimal performance and scalability.

### Cluster Setup

- **Cluster Tier**: Use at least `M10` or higher. Higher tiers support larger datasets and better performance.
- **Search Tier**: Use `S30` or higher to ensure sufficient memory and CPU for search workloads.
- **Node Architecture**: MongoDB (`mongod`) and Search (`mongot`) processes must run on separate nodes. This setup allows independent scaling and avoids resource conflicts.

### Cloud Provider and Region

Search Nodes are available across AWS, Azure, and Google Cloud, although not in all regions. Ensure your chosen region supports Search Nodes.

### Benefits of Dedicated Search Nodes

- **Workload Isolation**: Database and search workloads don’t compete for resources.
- **Independent Scaling**: You can scale search resources separately from the database.
- **Improved Query Performance**: Queries can run concurrently, especially on large datasets.

Example: If you have 1 million 768-dimensional vectors (~3 GB total), the `S30` (Low-CPU) or `S20` (High-CPU) search tier can handle the load. However, we recommend the `S20` tier for better query concurrency.

### Enable Encryption at Rest

To enhance security, you can enable **Encryption at Rest** using customer-managed keys on Search Nodes. Currently, this feature is supported only with AWS KMS.

### Migrating to Dedicated Search Nodes

To migrate from shared nodes to dedicated Search Nodes:

1. Upgrade to a cluster tier of `M10` or higher.
2. Ensure your cluster is deployed in a region that supports Search Nodes.
3. Enable and configure Search Nodes via the Atlas UI or API.

By following these guidelines, you can ensure a well-optimized deployment for your Atlas Vector Search applications, whether for testing, prototyping, or production.