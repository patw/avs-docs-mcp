# Build a Multi-Tenant Architecture for Atlas Vector Search

You can implement multi-tenancy with Atlas Vector Search so that a single instance of an application serves multiple tenants. This page describes design recommendations that apply specifically to Atlas Vector Search. These recommendations differ from our [multi-tenancy recommendations for Atlas](https://mongodb.com/docs/atlas/build-multi-tenant-arch/#std-label-build-multi-tenant-arch).

<div id="std-label-avs-multi-tenancy-recommendations"></div>

## Recommendations

Refer to the following recommendations when designing a multi-tenant architecture for Atlas Vector Search.

This guidance assumes that you can colocate tenants within a single VPC (Virtual Private Cloud). Otherwise, you must maintain separate projects for each tenant, which we don't recommend Atlas Vector Search.

<div id="std-label-avs-multi-tenancy-one-collection"></div>

### One Collection for all Tenants

We recommend storing **all tenant data in a single collection**, as well as in a single database and cluster. You can distinguish between tenants by including a `tenant_id` field within each document. This field can be any unique identifier for the tenant, such as a UUID or a tenant name. You can use this field as a [pre-filter](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/#std-label-vectorSearch-agg-pipeline-filter) in your Atlas Vector Search indexes and queries.

This centralized approach offers the following benefits:

- Easy to model and scale.

- Simplifies maintenance operations.

- Efficient query routing through pre-filtering by `tenant_id`.

  You are guaranteed to not serve tenants that do not match this filter.

### One Collection per Tenant

We do **not** recommend storing each tenant in a separate collection, as this approach might lead to varying [change stream](https://www.mongodb.com/docs/manual/changeStreams/) loads depending on the number of collections. This might negatively impact performance and monitoring capabilities. Data isolation guarantees in Atlas apply at the database level, so there is no additional data isolation benefit to using multiple collections.

Instead, use [one collection for all tenants](https://mongodb.com/docs/atlas/atlas-vector-search/multi-tenant-architecture/#std-label-avs-multi-tenancy-one-collection). For an example of how to migrate from a collection-per-tenant model to a single collection model, see [Migrating from a Collection-Per-Tenant Model](https://mongodb.com/docs/atlas/atlas-vector-search/multi-tenant-architecture/#std-label-multi-tenancy-migrate).

## Considerations

Consider the following strategies to mitigate potential performance issues with the [recommended approach](https://mongodb.com/docs/atlas/atlas-vector-search/multi-tenant-architecture/#std-label-avs-multi-tenancy-recommendations).

### Tenant Size Discrepancies

If you experience performance issues due to unequal distribution of data (some large tenants and many small tenants), use [MongoDB Views](https://mongodb.com/docs/atlas/atlas-vector-search/transform-documents-collections/#std-label-avs-transform-documents-collections) to separate large tenants from smaller tenants:

- **Large Tenants (Top 1%)**:

  - Create a view for each large tenant.

  - Create an index for each view.

  - Maintain a record of large tenants that you check at query-time to route queries accordingly.

- **Small Tenants (Remaining Tenants)**:

  - Create a single view for all small tenants.

  - Build a single index for this view.

  - Use the `tenant_id` field as a pre-filter to route queries accordingly.

#### Example

The following example demonstrates how to create views for large and small tenants by using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh):

<Tabs>

<Tab name="Large Tenants">

Keep a record of your large tenants and their corresponding `tenant_id` values, and then create a view for each of these tenants:

```shell
db.createView(
  "<viewName>",
  "<collectionName>",
  [
    {
      "$match": {
        "tenant_id": "<largeTenantId>"
      }
    }
  ]
)
```

</Tab>

<Tab name="Small Tenants">

Create a view for the small tenants, filtering out the large tenants:

```shell
db.createView(
  "<viewName>",
  "<collectionName>",
  [
    {
      "$match": {
        "tenant_id": {
          "$nin": [ "<largeTenantId1>", "<largeTenantId2>", ... ]
        }
      }
    }
  ]
)
```

</Tab>

</Tabs>

After creating the views, create the indexes for each view. Verify the following:

- When specifying the collection name for the index, use the view name instead of the original collection name.

- Ensure that your index on the small tenant view includes the `tenant_id` field as a pre-filter.

Refer to the [Create Indexes](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-type/#std-label-avs-types-vector-search) page for instructions on creating indexes.

### Many Large Tenants

If you have many tenants that each have a large number of vectors, consider using a partition-based system by distributing data across [shards](https://www.mongodb.com/docs/manual/core/sharded-cluster-shards/).

You can use the `tenant_id` field as a [shard key](https://www.mongodb.com/docs/manual/core/sharding-shard-key/) to distribute the data across specific ranges based on the tenant ID. For more information, see [Ranged Sharding](https://www.mongodb.com/docs/manual/core/ranged-sharding/).

<div id="std-label-multi-tenancy-migrate"></div>

### Migrating from a Collection-Per-Tenant Model

To migrate from a collection-per-tenant model to a single collection model, process each tenant collection and insert the documents into a new collection.

For example, the following script uses the [Node.js driver](https://www.mongodb.com/docs/drivers/node/) to migrate your data from a collection-per-tenant model to a single collection model. The script also includes a `tenant_id` field for each document based on the source collection's name.

```javascript
import { MongoClient } from 'mongodb';

const uri = "<connectionString>";
const sourceDbName = "<sourceDatabaseName>";
const targetDbName = "<targetDatabaseName>";
const targetCollectionName = "<targetCollectionName>";

async function migrateCollections() {
 const client = new MongoClient(uri);

 try {
     await client.connect();

     const sourceDb = client.db(sourceDbName);
     const targetDb = client.db(targetDbName);
     const targetCollection = targetDb.collection(targetCollectionName);

     const collections = await sourceDb.listCollections().toArray();
     console.log(`Found ${collections.length} collections.`);

     const BATCH_SIZE = 1000; // Define a suitable batch size based on your requirements
     let totalProcessed = 0;

     for (const collectionInfo of collections) {
         const collection = sourceDb.collection(collectionInfo.name);
         let documentsProcessed = 0;
         let batch = [];
         const tenantId = collectionInfo.name; // Uses the collection name as the tenant_id

         const cursor = collection.find({});
         for await (const doc of cursor) {
             doc.tenant_id = tenantId; // Adds a tenant_id field to each document
             batch.push(doc);

             if (batch.length >= BATCH_SIZE) {
                 await targetCollection.insertMany(batch);
                 totalProcessed += batch.length;
                 documentsProcessed += batch.length;
                 console.log(`Processed ${documentsProcessed} documents from ${collectionInfo.name}. Total processed: ${totalProcessed}`);
                 batch = [];
             }
         }

         if (batch.length > 0) {
             await targetCollection.insertMany(batch);
             totalProcessed += batch.length;
             documentsProcessed += batch.length;
             console.log(`Processed ${documentsProcessed} documents from ${collectionInfo.name}. Total processed: ${totalProcessed}`);
         }
     }

     console.log(`Migration completed. Total documents processed: ${totalProcessed}`);
 } catch (err) {
     console.error('An error occurred:', err);
 } finally {
     await client.close();
 }
}

await migrateCollections().catch(console.error);
```