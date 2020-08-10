#!/bin/bash

# Configure config file based on  environment variables

python modeling/etsicatalog/catalog/pub/config/config.py
cat modeling/etsicatalog/catalog/pub/config/config.py

function migrate_database {
    cd /service/modeling/etsicatalog
    python manage.py makemigrations
    python manage.py migrate
}

migrate_database

date > /service/init.log

# Start the microservice
/service/modeling/etsicatalog/docker/instance_run.sh
