#!/bin/bash

if [ "$DATABASE" = "postgresql" ]
then
    echo "Waiting for postgresql $SQL_HOST:$SQL_PORT ..."
    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done
    echo "PostgreSQL started"
fi

echo "Making and applying database migrations"
python manage.py makemigrations
python manage.py migrate

exec "$@"