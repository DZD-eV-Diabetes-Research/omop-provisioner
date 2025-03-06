# OMOP-provisioner

A helper container to prepare a [Postgres](https://www.postgresql.org/) database for using the [OMOP CDM](https://ohdsi.github.io/CommonDataModel/)

# About

The scope of this project is to help creating disposable/local/tinkering instances of the OMOP CDM with vocabulary running on a Postgres database and registering this database as a source for a [OHDSI/WebAPI](https://github.com/OHDSI/WebAPI) instance.

OMOP Provisioner is based on https://github.com/DZD-eV-Diabetes-Research/dzd-omop-cdm-python-models and build for https://github.com/DZD-eV-Diabetes-Research/atlas-testing-docker

# Usage

This projects aims to be used as a Docker container image

The image is hosted on https://hub.docker.com at [dzdde/omop-provisioner](https://hub.docker.com/r/dzdde/omop-provisioner)

Lets have an example how to integrate it in an `docker-compose.yaml` file

```yaml
networks:
  defaultnet:

services:
  omop-provision:
    image: dzdde/omop-provisioner
    environment:
      LOG_LEVEL: DEBUG
      POSTGRESQL_HOST: postgresql
      POSTGRESQL_USER: omop
      POSTGRESQL_DATABASE: omop
      POSTGRESQL_PASSWORD: omop
      POSTGRESQL_PORT: 5432
      VOCABULARY_SOURCE: https://my-storage.com/my-athena-export.zip
      LOAD_VOCABULARY: true
    depends_on:
      postgresql:
        condition: service_healthy
    networks:
      - defaultnet

  postgresql:
    image: postgres:16
    restart: always
    environment:
      - POSTGRES_PASSWORD=omop
      - POSTGRES_DB=omop
      - POSTGRES_USER=omop
    healthcheck:
      test: "pg_isready -h localhost -p 5432 -q -U omop"
      interval: 5s
      timeout: 5s
      retries: 5
  my-other-omop-service:
    image: my-other-omop-service
    depends_on:
      omop-provision:
        condition: service_completed_successfully
```

With the command `docker compose up` we will spin up a postgres database, deploy the OMOP CDM schema to this database and finaly load some Athena vocabulary from an URL.

Our imaginary software `my-other-omop-service` will start after all this is done and will have a ready to go OMOP schema available.

## configuration

For all configuration options have a look at the [`omop_provisioner/config.py`](omop_provisioner/config.py) file.

# Development

## Setup

requierments:

- [PDM](https://pdm-project.org/latest/)
- [Docker](https://www.docker.com/) with docker compose

Install all python dependencies:

`pdm install`

> [!NOTE]  
> If you don't want to use PDM and manage your env and modules more traditional, you can also install the dependencies via `python3 -m pip install -U -r requirements.txt`

## Start local smoke test

`./run_dev.sh`
