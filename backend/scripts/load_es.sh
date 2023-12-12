#!/bin/bash

DATA_DIR=$(dirname $(dirname $PWD))/data
docker-compose run -t --rm --entrypoint python -v $DATA_DIR:/data backend scripts/load_es.py
