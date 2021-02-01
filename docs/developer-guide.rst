.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Developer Guide
===============

Etsicatalog is a web application based on python3 and Django framework.

Pre-requisites
--------------

* Python3 & pip
* MariaDB

Etsicatalog can run standalone. However, if you want to try the whole functionality, you should have other components like SDC, DMaap(Non-mandatory), MSB(Non-mandatory) running.

You should set the component information in the environment variables as followed:
::

    SDC_ADDR=https://{SDC_IP}:30204
    MSB_ENABLED=true
    MSB_ADDR=https://{MSB_IP}:30283
    DMAAP_ENABLED=true
    DMAAP_ADDR=https://{DMAAP_IP}:30226

Note:

* The default value of MSB_ENABLED is **false**. Since Guilin Release, MSB is a **Non-mandatory** component. If you have no MSB installed or intention to use it, you can just omit MSB_ADDR and MSB_ENABLED.
* The default value of DMAAP_ENABLED is **false**. If you want to use SDC subscription and notification function, you should set it true and set DMAAP_ADDR properly.

Build & Run
-----------

**Clone repository**:
::

    $ git clone https://gerrit.onap.org/r/modeling/etsicatalog
    $ cd etsicatalog

**Create database**::

  $ cd /resources/dbscripts/mysql

Run modeling-etsicatalog-createdb.sql to create database.

Run commands followed to init database::

  $ python manage.py makemigrations
  $ python manage.py makemigrations database
  $ python manage.py migrate
  $ python manage.py migrate database

Review and edit \catalog\pub\config\config.py

MySQL default configuration is as follows::

    DB_IP = "127.0.0.1"
    DB_PORT = 3306
    DB_NAME = "etsicatalog"
    DB_USER = "etsicatalog"
    DB_PASSWD = "etsicatalog"

**Start server**::

  $ python manage.py runserver 8806



Test
----

**Run Healthcheck**::

    GET /api/catalog/v1/health_check

You should get::

    {
        "status": "active"
    }

**View API document**:

http://127.0.0.1:8806/api/catalog/v1/swagger


Run from Docker image
----------------------

You can run Modeling/etsicatalog directly from the docker image by following commands:
::

    $ docker run -d -p 3306:3306 --name etsicatalog-db -v /var/lib/mysql -e MYSQL_USER="etsicatalog" -e MYSQL_PASSWORD="etsicatalog" -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE="etsicatalog" nexus3.onap.org:10001/library/mariadb

    $ docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' etsicatalog-db
    Get the IP of etsicatalog-db

    $ docker run -d --name modeling-etsicatalog -v /var/lib/mysql -e DB_IP=<ip address> -e SDC_ADDR=<ip address> nexus3.onap.org:10001/onap/modeling/etsicatalog

**Note**:

You can also build the docker image instead of using the existed image from nexus3.onap.org:10001.
::

    $ cd docker
    $ docker build -t ${IMAGE_NAME} .