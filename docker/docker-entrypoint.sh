#!/bin/sh

python3 catalog/pub/config/config.py
python3 manage.py makemigrations
python3 manage.py migrate
date > /service/init.log

./run.sh

while [ ! -f logs/runtime_catalog.log ]; do
	sleep 1
done
tail -F logs/runtime_catalog.log
