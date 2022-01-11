# BSO Image Similarity
## About

This stack implements a [Pastec](https://github.com/swiss-art-research-net/pastec) instance and a service to use it within the [BSO](https://github.com/swiss-art-research-net/bso-data-pipeline) project 
## Usage

1. Copy provided `.env.example` file:
    * `cp .env.example .env`
1. Edit content of `.env` file if necessary
    * Refer to the comments in the `.env` file for the meaning of the configuration parameters
1. Make sure that the specified SPARQL endpoint is reachable from the Docker container. If necessary, connect the Docker container to the correct Docker network. This can be done manually or by creating a `docker-compose.override.yml`. For example:
    * ```yaml
      version: "3.3"
      services:
      pastec:
          networks:
          - default
      jobs:
          networks:
          - default
          - external_docker_network
      
      networks:
      default: null
      external_docker_network:
          name: bso-staging_default # Name of the external docker network
      ```

## Populate Index

```
docker exec bso_image_similarity_jobs task populate-index
```
