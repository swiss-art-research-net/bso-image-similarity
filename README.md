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

## Usage

The jobs service can be controlled through running tasks. To display a list of available tasks, run (change name of docker container, if required)
```bash
docker exec bso_image_similarity_jobs task --list
```
This will output a list of tasks:
```
task: Available tasks for this project:
* load-index:                   Load the index from a file
* populate-index:               Populate the Pastec index with image data from  BSO
* query-image:                  Search for an image in the Pastec index by URL
* retrieve-all-similar-images:  Query the database for image regions and retrieve all similar images
* save-index:                   Save the index to a file
```
Run a given task by specifying its name. For example, to populate the index, run:
```bash
docker exec bso_image_similarity_jobs task populate-index
```

##  Initialise

Load the index by running the `load-index` task:
```bash
docker exec bso_image_similarity_jobs task load-index
```

## Query

To look for similar images based on a single image, pass its URL to the `query-image` task:
```bash
docker exec bso_image_similarity_jobs task query-image -- https://bso-iiif.swissartresearch.net/iiif/2/nb-932619/full/800,/0/default.jpg                                                                                                                                                          (base) 
```
The above will return two sets of IRIs, the first one corresponding to the object, the second one to the IIIF Url. Currently this returns:
```
[('https://resource.swissartresearch.net/artwork/nb-932619', 'https://bso-iiif.swissartresearch.net/iiif/2/nb-932619'), ('https://resource.swissartresearch.net/artwork/zbz-990054763520205508', 'https://www.e-rara.ch/zuz/i3f/v20/15508247')]
```
Note that images already in the index will always return themselves.

The returned images are:
| iri  | image  |
|--|--|
|https://resource.swissartresearch.net/artwork/nb-932619|<img src="https://bso-iiif.swissartresearch.net/iiif/2/nb-932619/full/300,/0/default.jpg">|
|https://resource.swissartresearch.net/artwork/zbz-990054763520205508|<img src="https://www.e-rara.ch/zuz/i3f/v20/15508247/full/300,/0/default.jpg">|

The second image contains a colour bar. It is recommended to query using a crop of the image that excludes the colour bar. Otherwise, the query likely returns other images that contain the colour bar.
