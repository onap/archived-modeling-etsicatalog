#!/bin/bash

cd /service/modeling/toscaparsers/genericparser

./run.sh

while [ ! -f logs/runtime_catalog.log ]; do
    sleep 1
done
tail -F logs/runtime_catalog.log
