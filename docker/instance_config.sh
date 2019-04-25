#!/bin/bash

MSB_IP=`echo $MSB_ADDR | cut -d: -f 1`
MSB_PORT=`echo $MSB_ADDR | cut -d: -f 2`
# modeling/genericparser

if [ $MSB_IP ]; then
    sed -i "s|MSB_SERVICE_IP.*|MSB_SERVICE_IP = '$MSB_IP'|"  modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
fi

if [ $MSB_PORT ]; then
    sed -i "s|MSB_SERVICE_PORT.*|MSB_SERVICE_PORT = '$MSB_PORT'|" modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
fi

if [ $SERVICE_IP ]; then
    sed -i "s|\"ip\": \".*\"|\"ip\": \"$SERVICE_IP\"|" modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
fi

MYSQL_IP=`echo $MYSQL_ADDR | cut -d: -f 1`
MYSQL_PORT=`echo $MYSQL_ADDR | cut -d: -f 2`
echo "MYSQL_ADDR=$MYSQL_ADDR"

if [ $REDIS_ADDR ]; then
    REDIS_IP=`echo $REDIS_ADDR | cut -d: -f 1`
else
    REDIS_IP="$MYSQL_ADDR"
fi


sed -i "s|DB_IP.*|DB_IP = '$MYSQL_IP'|" modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
sed -i "s|DB_PORT.*|DB_PORT = $MYSQL_PORT|" modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
sed -i "s|REDIS_HOST.*|REDIS_HOST = '$REDIS_IP'|"modeling/toscaparsers/genericparser/genericparser/pub/config/config.py

cat modeling/toscaparsers/genericparser/genericparser/pub/config/config.py
