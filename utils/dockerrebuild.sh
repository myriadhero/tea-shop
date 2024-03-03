#! /usr/bin/bash
# this script should rebuild the containers
docker compose --profile prod build
docker compose --profile prod up -d

docker compose --profile prod exec web python manage.py migrate --noinput
docker compose --profile prod exec web python manage.py collectstatic --noinput

docker compose --profile prod restart web