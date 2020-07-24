#!/bin/bash

if [ -z "$SERVICE_IP" ]; then
    export SERVICE_IP=`hostname -i`
fi
echo "SERVICE_IP=$SERVICE_IP"

if [ -z "$MSB_ADDR" ]; then
    echo "Missing required variable MSB_ADDR: Microservices Service Bus address <ip>:<port>"
    exit 1
fi
echo "MSB_ADDR=$MSB_ADDR"

# Configure config file based on  environment variables

python modeling/etsicatalog/catalog/pub/config/config.py
cat modeling/etsicatalog/catalog/pub/config/config.py

# microservice-specific one-time initialization

MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`

if [ $MYSQL_ROOT_USER ] && [ $MYSQL_ROOT_PASSWORD ]; then
    MYSQL_ROOT_USER=$MYSQL_ROOT_USER
    MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
else
    MYSQL_ROOT_USER="root"
    MYSQL_ROOT_PASSWORD="root"
fi

function create_database {

    cd /service/modeling/etsicatalog/resources/bin
    bash initDB.sh $MYSQL_ROOT_USER $MYSQL_ROOT_PASSWORD $MYSQL_PORT $MYSQL_IP

 }

function migrate_database {
    cd /service/modeling/etsicatalog
    python manage.py migrate
}

create_database
migrate_database

date > /service/init.log

# Start the microservice
/service/modeling/etsicatalog/docker/instance_run.sh
