# Troubleshooting

This document provides advice for troubleshooting problems with Atlas Vector Search. For direct assistance with Atlas Vector Search issues, you can either start a discussion on the [MongoDB Developer Community](https://www.mongodb.com/community/forums/c/atlas/vector-search/168) or [contact support](https://mongodb.com/docs/atlas/support/#std-label-request-support).

## Cannot use the `$vectorSearch` stage on Atlas cluster

To use the `$vectorSearch` pipeline stage to query your cluster, your cluster must run MongoDB 6.0.11+ or 7.0.2+. If you invoke `$vectorSearch` on an incompatible version of MongoDB, you might see the following error:

```sh
OperationFailure: $vectorSearch is not allowed with the current
configuration. You may need to enable the corresponding feature
flag.
```

To check the MongoDB version of your cluster:

### In Atlas, go to the Clusters page for your project.

We're currently rolling out a new and improved navigation experience. If the following steps don't match your view in the Atlas UI, see [the preview documentation](https://dochub.mongodb.org/core/atlas-nav-preview).

- If it's not already displayed, select the organization that contains your desired project from the  Organizations menu in the navigation bar.

- If it's not already displayed, select your desired project from the Projects menu in the navigation bar.

- If it's not already displayed, click Clusters in the sidebar.

  The [Clusters](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters) page displays.

Locate the information pane of the cluster you want to use `$vectorSearch` on.

Consult the Version number in the bottom section of the information pane.

If your cluster runs a version of MongoDB earlier than 6.0.11 or 7.0.2, you must [upgrade the MongoDB version of the cluster](https://mongodb.com/docs/atlas/scale-cluster/#std-label-scale-cluster-version).

## Slow queries

For recommendations on improving query performance, see [Improve Vector Search Performance](https://mongodb.com/docs/atlas/atlas-vector-search/tune-vector-search/#std-label-avs-performance-tuning).

## `$vectorSearch` returns no results

If `$vectorSearch` queries return no results, perform the following actions:

- Ensure that you're using the same embedding model for both your data and your query. If you embed your query using a different model than you use to embed your data, `$vectorSearch` can't identify matches.

- Ensure that your Atlas Vector Search has finished building. When you create or update an Atlas Vector Search index, the index the index is in an [initial sync](https://mongodb.com/docs/atlas/atlas-search/performance/index-performance/#std-label-troubleshoot-initial-sync) state. When it finishes building, you can start querying the data in your collection.

## `Error during document retrieval` when using filtering with LangChain

When you use LangChain to perform RAG (Retrieval-Augmented Generation) with pre-filtering, you might encounter the following error:

```js
Error during the document retrieval or generation process:
MongoServerError: PlanExecutor error during aggregation :: caused
by :: Path 'field' needs to be indexed as token
```

If an index on `field` exists, ensure you have created this index as an Atlas Vector Search index, not an Atlas Search index. If no index on `field` exists, [create one](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/#std-label-avs-create-index). To learn more about implementing RAG (Retrieval-Augmented Generation) with Atlas Vector Search and LangChain, see [Answer Questions on Your Data](https://mongodb.com/docs/atlas/ai-integrations/langchain/get-started/#std-label-langchain-rag).

## `Command not found` when creating Atlas Vector Search index

When you attempt to create an Atlas Vector Search index programmatically, you might encounter a `Command not found` error. This error occurs for one of two reasons:

- You run the command against an Atlas cluster running a version of MongoDB earlier than 6.0.11 or 7.0.2. In this case, you must [upgrade the MongoDB version of the cluster](https://mongodb.com/docs/atlas/scale-cluster/#std-label-scale-cluster-version) to enable Atlas Vector Search for the cluster.

- You run the command against an `M0` Free Tier cluster. In this case, as long as the cluster is running a compatible MongoDB version, you can [create an Atlas Vector Search index with the Atlas UI](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/#std-label-avs-create-index-procedure).

## Unable to filter on a given field

Atlas Vector Search currently supports filtering only on fields with boolean, date, number, objectId, string, and UUID values. To learn more, see [About the `filter` Type](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/#std-label-avs-types-filter).