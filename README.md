# About

This stack implements a [Pastec](https://github.com/swiss-art-research-net/pastec) instance and a service to use it within the [BSO](https://github.com/swiss-art-research-net/bso-data-pipeline) project 

## Prerequisites

Assumes a Blazegraph endpoint is accessible at http://blazegraph:8080/blazegraph/sparql. Connect the Docker container to the correct Docker network if necessary
## Populate Index

```
docker exec bso_image_similarity_jobs task populate-index
```
