#!/bin/sh
set -eu

# Run from DockerMongo, regardless of the caller's current directory.
cd "$(dirname "$0")/.."

docker compose up -d db
docker compose run --build --rm --no-deps web python -m unittest discover -s tests -v
