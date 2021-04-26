#!/bin/sh

python catalog/pub/config/config.py
python manage.py makemigrations 
python manage.py migrate 
date > /service/init.log

./run.sh
while [ ! -f logs/runtime_catalog.log ]; do
	sleep 1
done
tail -F logs/runtime_catalog.log
