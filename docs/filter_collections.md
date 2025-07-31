# Use MongoDB Views to Transform Documents and Filter Collections for Atlas Vector Search

Atlas Vector SearchYou can create an Atlas Vector Search index on a [View](https://www.mongodb.com/docs/manual/core/views/) to transform documents and collections so that you can partially index a collection, support incompatible data types or data models, and more.

Using MongoDB Views with Atlas Vector Search is available as a Preview feature. The feature and the corresponding documentation might change at any time during the Preview period. To learn more, see [Preview Features](https://www.mongodb.com/docs/preview-features/).

The following examples use the [sample_mflix](https://mongodb.com/docs/atlas/sample-data/sample-mflix/#std-label-sample-mflix) sample database.

This page discusses standard views. To learn about on-demand materialized views, see [On-Demand Materialized Views](https://www.mongodb.com/docs/manual/core/materialized-views/#std-label-manual-materialized-views).

To learn about the differences between the view types, see [Comparison with On-Demand Materialized Views](https://www.mongodb.com/docs/manual/core/views/#std-label-view-materialized-view-compare).

## Requirements

You must use:

- MongoDB 8.0 or higher.

During the Preview period, you must use:

- [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh) or [Compass](https://www.mongodb.com/docs/compass/current/) to create and manage MongoDB Views.

- Atlas UI and the Atlas Administration API to create Atlas Vector Search indexes on Views.  Support for [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh), [Compass](https://www.mongodb.com/docs/compass/current/), and [Drivers](https://www.mongodb.com/docs/drivers/) will be available when this feature is Generally Available.

To edit a View, you must have a [User Admin](https://www.mongodb.com/docs/manual/tutorial/configure-scram-client-authentication/#std-label-create-user-admin) role and use the [`collMod`](https://www.mongodb.com/docs/manual/reference/command/collMod/#mongodb-dbcommand-dbcmd.collMod) database command.

## Limitations

- Atlas Vector Search supports Views only for [`$expr`](https://www.mongodb.com/docs/manual/reference/operator/query/expr/#mongodb-query-op.-expr) in the following stages:

  - [`$addFields`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/addFields/#mongodb-pipeline-pipe.-addFields)

  - [`$set`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/set/#mongodb-pipeline-pipe.-set)

  - [`$match`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/match/#mongodb-pipeline-pipe.-match)

- Index names must be unique across a source collection and all of its Views.

- Atlas Vector Search doesn't support [view definitions](https://www.mongodb.com/docs/manual/core/views/) with operators that produce dynamic results, such as the [$$USER_ROLES](https://www.mongodb.com/docs/manual/reference/aggregation-variables/#mongodb-variable-variable.USER_ROLES) system variable and the [$rand](https://www.mongodb.com/docs/manual/reference/operator/aggregation/rand/) aggregation operator.

- Atlas Vector Search queries return the original documents as they appear in the source collection.

## Example: Filter Documents

To create a View, you must have the [`createCollection`](https://www.mongodb.com/docs/manual/reference/privilege-actions/#mongodb-authaction-createCollection) privilege.

You can filter documents to partially index a collection. The following example creates a View on the `sample_mflix.embedded_movies` collection so that only documents that have a vector embedding field are indexed.

Atlas Vector Search`embeddingsIndex``sample_mflix``moviesWithEmbeddings``embedded_movies`### Connect to the Atlas cluster using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh).

To learn more, see [Connect via `mongosh`](https://mongodb.com/docs/atlas/mongo-shell-connection/#std-label-connect-mongo-shell).

### Switch to the `sample_mflix` database.

```sh
use sample_mflix
```

### Create a `moviesWithEmbeddings` View.

```sh
db.createView(
  "moviesWithEmbeddings",
  "embedded_movies",
  [
    {
      "$match": {
        "$expr": {
          "$ne": [
            {
              "$type": "$plot_embedding"
            },
            "missing"
          ]
        }
      }
    }
  ]
)
```

### In Atlas, go to the Clusters page for your project.

We're currently rolling out a new and improved navigation experience. If the following steps don't match your view in the Atlas UI, see [the preview documentation](https://dochub.mongodb.org/core/atlas-nav-preview).

- If it's not already displayed, select the organization that contains your desired project from the  Organizations menu in the navigation bar.

- If it's not already displayed, select your desired project from the Projects menu in the navigation bar.

- If it's not already displayed, click Clusters in the sidebar.

  The [Clusters](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters) page displays.

### Go to the Atlas Search page for your cluster.

You can go the Atlas Search page from the sidebar, the Data Explorer, or your cluster details page.

<Tabs>

<Tab name="Sidebar">

- In the sidebar, click Atlas Search under the Services heading.

  If you have no clusters, click Create cluster to create one. To learn more, see [Create a Cluster](https://mongodb.com/docs/atlas/tutorial/create-new-cluster/#std-label-create-new-cluster).

- If your project has multiple clusters, select the cluster you want to use from the Select cluster dropdown, then click Go to Atlas Search.

  The [Atlas Search](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters%2FatlasSearch%2F%3Ccluster%3E) page displays.

</Tab>

<Tab name="Data Explorer">

- Click the Browse Collections button for your cluster.

- Expand the database and select the collection.

- Click the Search Indexes tab for the collection.

  The [Atlas Search](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters%2FatlasSearch%2F%3Ccluster%3E%3Fdatabase%3Dsample_mflix%26collectionName%3Dusers) page displays.

</Tab>

<Tab name="Cluster Details">

- Click the cluster's name.

- Click the Atlas Search tab.

  The [Atlas Search](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters%2FatlasSearch%2F%3Ccluster%3E) page displays.

</Tab>

</Tabs>

### Click Create Search Index.

### Click Create Search Index.

### Start your index configuration.

Make the following selections on the page and then click Next.

<table>

<tr>
<td>
Search Type

</td>
<td>
Select the Atlas Vector Search index type.

</td>
</tr>
<tr>
<td>
Index Name and Data Source

</td>
<td>
Specify the following information:

- Index Name: `embeddingsIndex`

- Database and Collection:

  - `sample_mflix`

  - `moviesWithEmbeddings`

</td>
</tr>
<tr>
<td>
Configuration Method

</td>
<td>
For a guided experience, select Visual Editor.To edit the raw index definition, select JSON Editor.

</td>
</tr>
</table>Your Atlas Search index is named `default` by default. If you keep this name, then your index will be the default Search index for any Atlas Search query that does not specify a different `index` option in its [operators](https://mongodb.com/docs/atlas/atlas-search/operators-and-collectors/#std-label-fts-operators). If you are creating multiple indexes, we recommend that you maintain a consistent, descriptive naming convention across your indexes.

### Specify an index definition.

- Specify the following index definition:

  ```json
  {
    "fields": [
      {
        "type": "vector",
        "numDimensions": 1536,
        "path": "plot_embedding",
        "similarity": "cosine"
      }
    ]
  }
  ```

- Click Next.

### Click Create Vector Search Index.

Atlas displays a modal window to let you know your index is building.

### Close the You're All Set! Modal Window by clicking the Close button.

### Check the status.

The newly created index displays on the Atlas Search tab. While the index is building, the Status field reads Build in Progress. When the index is finished building, the Status field reads Active.

Larger collections take longer to index. You will receive an email notification when your index is finished building.

### Run a query on the `embeddingsIndex` partial index.

The following example queries the `embeddingsIndex` index by running the `.aggregate` command against the source collection `embedded_movies`. During the Preview period, you must query search indexes created on Views using the source collection (`embedded_movies`) of the View. If you query the View (`moviesWithEmbeddings`), Atlas Vector Search returns no results.

```sh
use sample_mflix
```

```sh
db.embedded_movies.aggregate([
  {
    "$vectorSearch": {
      "index": "embeddingsIndex",
      "path": "plot_embedding",
      "queryVector": [-0.0016261312, -0.028070757, ...],
      "numCandidates": 100,
      "limit": 10
    }
  },
  {
    "$project": {
      "_id": 0,
      "plot": 1,
      "title": 1,
    }
  }
])
```

```sh
[
  {
    "plot" : "A reporter, learning of time travelers visiting 20th century disasters, tries to change the history they know by averting upcoming disasters.",
    "title" : "Thrill Seekers"
  },
  {
    "plot" : "At the age of 21, Tim discovers he can travel in time and change what happens and has happened in his own life. His decision to make his world a better place by getting a girlfriend turns out not to be as easy as you might think.",
    "title" : "About Time"
  },
  {
    "plot" : "Hoping to alter the events of the past, a 19th century inventor instead travels 800,000 years into the future, where he finds humankind divided into two warring races.",
    "title" : "The Time Machine"
  },
  {
    "plot" : "After using his mother's newly built time machine, Dolf gets stuck involuntary in the year 1212. He ends up in a children's crusade where he confronts his new friends with modern techniques...",
    "title" : "Crusade in Jeans"
  },
  {
    "plot" : "An officer for a security agency that regulates time travel, must fend for his life against a shady politician who has a tie to his past.",
    "title" : "Timecop"
  },
  {
    "plot" : "A time-travel experiment in which a robot probe is sent from the year 2073 to the year 1973 goes terribly wrong thrusting one of the project scientists, a man named Nicholas Sinclair into a...",
    "title" : "A.P.E.X."
  },
  {
    "plot" : "Agent J travels in time to M.I.B.'s early days in 1969 to stop an alien from assassinating his friend Agent K and changing history.",
    "title" : "Men in Black 3"
  },
  {
    "plot" : "Bound by a shared destiny, a teen bursting with scientific curiosity and a former boy-genius inventor embark on a mission to unearth the secrets of a place somewhere in time and space that exists in their collective memory.",
    "title" : "Tomorrowland"
  },
  {
    "plot" : "With the help of his uncle, a man travels to the future to try and bring his girlfriend back to life.",
    "title" : "Love Story 2050"
  },
  {
    "plot" : "A dimension-traveling wizard gets stuck in the 21st century because cell-phone radiation interferes with his magic. With his home world on the brink of war, he seeks help from a jaded ...",
    "title" : "The Portal"
  }
]
```

## Performance Considerations

For indexes created on views, Atlas Vector Search applies the transformations or filters that you define in the view pipeline at query-time and at replication-time. While trivial transformations or filters in the view pipeline typically result in negligible performance impact, complex transformations or highly selective filters in the view pipeline might significantly slow down querying or replication. If you want to perform a heavy transformation on the documents or apply a highly selective filter, consider creating a materialized view with already transformed or filtered documents. You can evaluate view performance by comparing query latency executed against the view and against its source collection.

## Troubleshoot

Indexes change to the `FAILED` status in the following scenarios:

- You create an index on a View that is incompatible with Atlas Vector Search.

- You edit a View in a way that does not meet the Atlas Vector Search compatibility requirements.

- You remove or change a View's source collection.

  For example, if one View is created on another View, and you change the parent View source to another collection.

  This limitation also applies if a View is a descendent of other Views. For example, you can't change or remove the source collection that all descendents originate from.

Indexes stall in the following scenarios:

If the aggregation pipeline defined in your View is incompatible with the documents in the collection, search replication fails. For example, if a `$toDouble` expression operates on a document field that contains an array, the replication fails. Ensure your View works with all documents in the collection without errors.

- If the View definition causes an aggregation failure while an index is `READY`, the index becomes `STALE`. The index will return to `READY` after you resolve the document or change the view definition so that it doesn't fail anymore. However, the index is queryable until the replication is automatically removed from the [oplog](https://www.mongodb.com/docs/manual/reference/glossary/#std-term-oplog).

- If the View definition causes an aggregation pipeline failure while the index is `BUILDING`, the index build is stuck until you fix the document. The index will return to `READY` after you resolve the document or change the view definition so that it doesn't fail anymore.

You can view index statuses in the Atlas UI on the [index status details](https://mongodb.com/docs/atlas/atlas-search/manage-indexes/#std-label-queryable-index) page.

## Index Process

When you create an Atlas Vector Search index on a View, the `mongot` process performs the same tasks as when you create an Atlas Vector Search index on a regular collection. The `mongot` process:

1. Creates Atlas Vector Search indexes based on the rules in the index definition for the collection.

2. Monitors change streams for the current state of the documents and indexes for the collections for which you defined the Atlas Vector Search indexes.

3. Processes Atlas Vector Search queries and returns the document IDs and other search metadata for the matching documents to `mongod`, which then does a full document lookup and returns the results to the client.

When you create an Atlas Vector Search index on a View, the View definition is applied during Step 1 and 2, and the transformed documents are stored in the Atlas Vector Search index on disk.

## Learn More

To learn more about Views, see [Views](https://www.mongodb.com/docs/manual/core/views/).

To create an Atlas Search index on a View, see [Use MongoDB Views to Transform Documents and Filter Collections for Atlas Search](https://mongodb.com/docs/atlas/atlas-search/transform-documents-collections/#std-label-fts-transform-documents-collections).