# How to Measure the Accuracy of Your Query Results

You can measure the accuracy of your Atlas Vector Search query by evaluating how closely the results for an ANN (Approximate Nearest Neighbor) search match the results of an ENN (Exact Nearest Neighbor) search against quantized vectors by using the same query criteria. That is, you can compare the results of ANN (Approximate Nearest Neighbor) search with the results of ENN (Exact Nearest Neighbor) search and measure how frequently the ANN (Approximate Nearest Neighbor) search results include the nearest neighbors in the results from the ENN (Exact Nearest Neighbor) search.

## Use Cases

You might want to measure the accuracy of the results if you have any of the following:

- Quantized vectors

- Large numbers of vectors

- Low dimensional vectors

## Prerequisites

To try the examples on this page, you need the following:

- An Atlas cluster with, optionally, the sample dataset.

- [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh)

## Procedures

To evaluate the accuracy of your [`$vectorSearch`](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/#mongodb-pipeline-pipe.-vectorSearch) query results, you must do the following:

1. Create an Atlas Vector Search index on the vector field and on any other fields that you want to pre-filter the data by.

   We recommend using quantized vectors to improve the storage of your vectors and speed of your queries. If you don't have quantized vectors, you can enable automatic quantization when indexing your `vector` type field.

2. Construct and run the ENN (Exact Nearest Neighbor) query followed by the ANN (Approximate Nearest Neighbor) query.

3. Compare the results of the ANN (Approximate Nearest Neighbor) query with the results of the ENN (Exact Nearest Neighbor) query to evaluate the similarities and differences in the results.

This section demonstrates how to perform the preceding 3 steps against data in the `sample_mflix.embedded_movies` collection. If you don't wish to use the sample dataset, you can perform the procedures against your own data.

### Create the Atlas Vector Search Index

This section demonstrates how to create an Atlas Vector Search index for running Atlas Vector Search ANN (Approximate Nearest Neighbor) and ENN (Exact Nearest Neighbor) queries.

Vector Search`vector_index``sample_mflix` database`embedded_movies` collection`sample_mflix.embedded_movies``plot_embedding`EuclideanBinary`genres` field#### In Atlas, go to the Clusters page for your project.

We're currently rolling out a new and improved navigation experience. If the following steps don't match your view in the Atlas UI, see [the preview documentation](https://dochub.mongodb.org/core/atlas-nav-preview).

- If it's not already displayed, select the organization that contains your desired project from the  Organizations menu in the navigation bar.

- If it's not already displayed, select your desired project from the Projects menu in the navigation bar.

- If it's not already displayed, click Clusters in the sidebar.

  The [Clusters](https://cloud.mongodb.com/go?l=https%3A%2F%2Fcloud.mongodb.com%2Fv2%2F%3Cproject%3E%23%2Fclusters) page displays.

#### Go to the Atlas Search page for your cluster.

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

#### Click Create Search Index.

#### Start your index configuration.

Make the following selections on the page and then click Next.

<table>

<tr>
<td>
Search Type

</td>
<td>
Select the Vector Search index type.

</td>
</tr>
<tr>
<td>
Index Name and Data Source

</td>
<td>
Specify the following information:

- Index Name: `vector_index`

- Database and Collection:

  - `sample_mflix` database

  - `embedded_movies` collection

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

#### Specify the index definition.

This index definition indexes the `plot_embedding` field as the `vector` type with automatic binary `quantization` enabled and the `genres` field as the `filter` type in an Atlas Vector Search index. The `plot_embedding` field contains embeddings created using OpenAI's `text-embedding-ada-002` embeddings model. The index definition specifies `1536` vector dimensions and measures distance using `euclidean` similarity function.

<Tabs>

<Tab name="Visual Editor">

Atlas automatically detects fields that contain vector embeddings, as well as their corresponding dimensions. For the `sample_mflix.embedded_movies` collection, the `plot_embedding` field displays.

To configure the index, do the following:

- Select Euclidean from the Similarity Method dropdown.

- Click Advanced, then select Binary quantization from the dropdown menu.

- In the Filter Field section, specify the `genres` field to filter the data by.

</Tab>

<Tab name="JSON Editor">

Paste the following index definition in the JSON editor:

```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "plot_embedding",
      "similarity": "euclidean",
      "type": "vector",
      "quantization": "binary"
    },
    {
      "path": "genres",
      "type": "filter"
    }
  ]
}
```

</Tab>

</Tabs>

#### Click Next to review the index.

#### Click Create Vector Search Index.

Atlas displays a modal window to let you know your index is building.

#### Close the You're All Set! Modal Window by clicking the Close button.

#### Check the status.

The newly created index displays on the Atlas Search tab. While the index is building, the Status field reads Build in Progress. When the index is finished building, the Status field reads Active.

Larger collections take longer to index. You will receive an email notification when your index is finished building.

### Run the Queries

This section demonstrates how to run the ENN (Exact Nearest Neighbor) and ANN (Approximate Nearest Neighbor) queries against the indexed collection.

#### Connect to your Atlas cluster using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh).

Open a terminal window and connect to your cluster by using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh). To learn more, see [Connect via `mongosh`](https://mongodb.com/docs/atlas/mongo-shell-connection/#std-label-connect-mongo-shell).

#### Switch to your database.

Use the `sample_mflix` database. To switch to the `sample_mflix` database, run the following command at [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh) prompt:

```sh
use sample_mflix
```

```sh
switched to db sample_mflix
```

#### Run your ENN (Exact Nearest Neighbor) query.

Copy and paste the following sample query into your terminal and then run it using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh). [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh) might lag slightly when you paste in the query due to the number of characters in the vector embedding.

```shell
db.embedded_movies.aggregate([
  {
    "$vectorSearch": {
      "index": "vector_index",
      "path": "plot_embedding",
      "filter": {
        "$and": [
          {
            "genres": { "$eq": "Action" }
          },
          {
            "genres": { "$ne": "Western" }
          }
        ]
      },
      "queryVector": [-0.0241895392537117, -0.01683979481458664, ..., 4.4379456085152924e-05, -3.941043178201653e-05, -0.0048729064874351025, -0.033356525003910065, ..., -5.947057798039168e-05, -0.011239991523325443, 0.006791108753532171, ..., 4.68508260382805e-05, 0.019451241940259933, -0.018495507538318634, ..., -1.4092055607761722e-05, -0.011388063430786133, 0.01671864651143551, ...],
      "exact": true,
      "limit": 10
    }
  },
  {
    "$project": {
      "_id": 0,
      "plot": 1,
      "title": 1,
      "genres": 1,
      "score": { $meta: "vectorSearchScore" }
    }
  }
])
```

```shell
[
  {
    plot: "A thief with a unique code of professional ethics is double-crossed by his crew and left for dead. Assuming a new disguise and forming an unlikely alliance with a woman on the inside, he looks to hijack the score of the crew's latest heist.",
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'Parker',
    score: 0.7952193021774292
  },
  {
    plot: 'An adrenaline junkie walks away from a whirlwind romance and embraces a new life as a thief, though he soon finds himself pursued by veteran police officer and engaged in a turf war with a local gangster.',
    genres: [ 'Action', 'Comedy', 'Romance' ],
    title: 'Kick',
    score: 0.7876788377761841
  },
  {
    plot: 'The dying words of a thief spark a madcap cross-country rush to find some treasure.',
    genres: [ 'Action', 'Adventure', 'Comedy' ],
    title: "It's a Mad, Mad, Mad, Mad World",
    score: 0.7861514687538147
  },
  {
    plot: 'A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist.',
    genres: [ 'Action', 'Crime', 'Drama' ],
    title: 'Heat',
    score: 0.7858744859695435
  },
  {
    plot: 'A romantic and action packed story of three best friends, a group of high end art thieves, who come into trouble when a love-triangle forms between them.',
    genres: [ 'Action', 'Comedy', 'Crime' ],
    title: 'Once a Thief',
    score: 0.7815249562263489
  },
  {
    plot: 'A recently released ex-con and his loyal wife go on the run after a heist goes awry.',
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'The Getaway',
    score: 0.7795301079750061
  },
  {
    plot: "The story of what happens after a master thief achieves his last big score, when the FBI agent who promised he'd capture him is about to do just that.",
    genres: [ 'Action', 'Comedy', 'Crime' ],
    title: 'After the Sunset',
    score: 0.779007613658905
  },
  {
    plot: 'A group of bank robbers find their multi-million dollar plan interrupted by a hard-boiled detective.',
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'Takers',
    score: 0.7787627577781677
  },
  {
    plot: "After he's shot during a heist in East L.A., an armored truck driver wrestles with rehabilitation and tracking down the man who committed the crime.",
    genres: [ 'Action', 'Crime', 'Drama' ],
    title: 'The Take',
    score: 0.7776619791984558
  },
  {
    plot: 'While doing a friend a favor and searching for a runaway teenager, a police detective stumbles upon a bizarre band of criminals about to pull off a bank robbery.',
    genres: [ 'Action', 'Crime', 'Drama' ],
    title: 'No Good Deed',
    score: 0.7773410677909851
  }
]
```

This query uses the following pipeline stages:

<table>

<tr>
<td>
[`$vectorSearch`](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/#mongodb-pipeline-pipe.-vectorSearch)

</td>
<td>
- Prefilters the documents to search for movies in the `Action` genre, and not in the `Western` genre.

- Searches the `plot_embedding` field for exact nearest neighbors by using vector embeddings for the string `thrilling heist with twists`.

- Limits the output to only 10 results.

</td>
</tr>
<tr>
<td>
[`$project`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/project/#mongodb-pipeline-pipe.-project)

</td>
<td>
- Excludes all fields except `plot`, `title`, and `genres` from the documents in the results.

- Adds a field named `score` that shows the score of the documents the results.

</td>
</tr>
</table>

#### Run your ANN (Approximate Nearest Neighbor) query.

Copy and paste the following sample query into your terminal and then run it using [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh). [`mongosh`](https://www.mongodb.com/docs/mongodb-shell/#mongodb-binary-bin.mongosh) might lag slightly when you paste in the query due to the number of characters in the vector embedding.

```shell
db.embedded_movies.aggregate([
  {
    "$vectorSearch": {
      "index": "vector_index",
      "path": "plot_embedding",
      "filter": {
        "$and": [
          {
            "genres": { "$eq": "Action" }
          },
          {
            "genres": { "$ne": "Western" }
          }
        ]
      },
      "queryVector": [-0.0241895392537117, -0.01683979481458664, ..., 4.4379456085152924e-05, -3.941043178201653e-05, -0.0048729064874351025, -0.033356525003910065, ..., -5.947057798039168e-05, -0.011239991523325443, 0.006791108753532171, ..., 4.68508260382805e-05, 0.019451241940259933, -0.018495507538318634, ..., -1.4092055607761722e-05, -0.011388063430786133, 0.01671864651143551, ...],
      "numCandidates": 100,
      "limit": 10
    }
  },
  {
    "$project": {
      "_id": 0,
      "plot": 1,
      "title": 1,
      "genres": 1,
      "score": { $meta: "vectorSearchScore" }
    }
  }
])
```

```shell
[
  {
    plot: "A thief with a unique code of professional ethics is double-crossed by his crew and left for dead. Assuming a new disguise and forming an unlikely alliance with a woman on the inside, he looks to hijack the score of the crew's latest heist.",
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'Parker',
    score: 0.7952193021774292
  },
  {
    plot: 'An adrenaline junkie walks away from a whirlwind romance and embraces a new life as a thief, though he soon finds himself pursued by veteran police officer and engaged in a turf war with a local gangster.',
    genres: [ 'Action', 'Comedy', 'Romance' ],
    title: 'Kick',
    score: 0.7876788377761841
  },
  {
    plot: 'The dying words of a thief spark a madcap cross-country rush to find some treasure.',
    genres: [ 'Action', 'Adventure', 'Comedy' ],
    title: "It's a Mad, Mad, Mad, Mad World",
    score: 0.7861514687538147
  },
  {
    plot: 'A group of professional bank robbers start to feel the heat from police when they unknowingly leave a clue at their latest heist.',
    genres: [ 'Action', 'Crime', 'Drama' ],
    title: 'Heat',
    score: 0.7858744859695435
  },
  {
    plot: 'A romantic and action packed story of three best friends, a group of high end art thieves, who come into trouble when a love-triangle forms between them.',
    genres: [ 'Action', 'Comedy', 'Crime' ],
    title: 'Once a Thief',
    score: 0.7815249562263489
  },
  {
    plot: 'A recently released ex-con and his loyal wife go on the run after a heist goes awry.',
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'The Getaway',
    score: 0.7795301079750061
  },
  {
    plot: "The story of what happens after a master thief achieves his last big score, when the FBI agent who promised he'd capture him is about to do just that.",
    genres: [ 'Action', 'Comedy', 'Crime' ],
    title: 'After the Sunset',
    score: 0.779007613658905
  },
  {
    plot: 'A group of bank robbers find their multi-million dollar plan interrupted by a hard-boiled detective.',
    genres: [ 'Action', 'Crime', 'Thriller' ],
    title: 'Takers',
    score: 0.7787627577781677
  },
  {
    plot: "After he's shot during a heist in East L.A., an armored truck driver wrestles with rehabilitation and tracking down the man who committed the crime.",
    genres: [ 'Action', 'Crime', 'Drama' ],
    title: 'The Take',
    score: 0.7776619791984558
  },
  {
    plot: 'A high-tech police surveillance team attempts to take down a gang of ruthless bank robbers.',
    genres: [ 'Action', 'Crime' ],
    title: 'Cold Eyes',
    score: 0.775409996509552
  }
]
```

This query uses the following pipeline stages:

<table>

<tr>
<td>
[`$vectorSearch`](https://mongodb.com/docs/atlas/atlas-vector-search/vector-search-stage/#mongodb-pipeline-pipe.-vectorSearch)

</td>
<td>
- Prefilters the documents to search by movies in the `Action` genre, and not in the `Western` genre.

- Searches the `plot_embedding` field for approximate nearest neighbors by using vector embeddings for the string `thrilling heist with twists`.

- Considers up to `100` nearest neighbors, but limits the output to only 10 results.

</td>
</tr>
<tr>
<td>
[`$project`](https://www.mongodb.com/docs/manual/reference/operator/aggregation/project/#mongodb-pipeline-pipe.-project)

</td>
<td>
- Excludes all fields except `plot`, `title`, and `genres` from the documents in the results.

- Adds a field named `score` that shows the score of the documents the results.

</td>
</tr>
</table>

### Compare the Results

The top nine documents in the example ENN (Exact Nearest Neighbor) and ANN (Approximate Nearest Neighbor) query results are the same and have the same score. This shows a high-level of similarity in the top results for the query. However, the tenth document in the ENN (Exact Nearest Neighbor) and ANN (Approximate Nearest Neighbor) query results is different, which reflects a slight variation in the exact and approximate nearest neighbor search.

ENN (Exact Nearest Neighbor) search examines all possible candidates and returns the closest match to the query based on the similarity score. ANN (Approximate Nearest Neighbor) search uses approximations to speed up the search, which might alter the score of the documents. If you increase the `numCandidates` value in the ANN (Approximate Nearest Neighbor) query, the results will be a closer match to the ENN (Exact Nearest Neighbor) query results. However, this would consume additional computational resources and might reduce query speed. The tenth document in the results reflects the trade-off between accuracy and speed.

After quantitatively evaluating results against the ENN (Exact Nearest Neighbor) ground truth, we recommend testing a set of 100 queries in the same manner and computing the "jaccard similarity" between the result sets. Jaccard similarity can be computed by dividing the intersection between two sets, that is, the overlapping items, by the total set size. This gives a sense for recall performance of ANN (Approximate Nearest Neighbor) queries, including those performed against quantized vectors.

If you notice large discrepancies between your ENN (Exact Nearest Neighbor) and ANN (Approximate Nearest Neighbor) query results, we recommend tuning the `numCandidates` value to strike an ideal balance between accuracy and speed for your application.

We recommend that you use judgement lists for a structured list of queries with their ideal results for the ANN (Approximate Nearest Neighbor) query or ENN (Exact Nearest Neighbor) ground truth values. You can use the ENN (Exact Nearest Neighbor) query results as the baseline judgement list and then evaluate ANN (Approximate Nearest Neighbor) query results against this judgement list to measure recall, overlap, and performance. Judgment lists provide a way to evaluate whether ANN (Approximate Nearest Neighbor) queries meet the desired accuracy or recall thresholds compared to the ENN (Exact Nearest Neighbor) baseline. Use LLMs to generate the example queries.