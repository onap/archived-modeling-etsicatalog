.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Installation
============

This document describes local build and installation for development purpose.

Pre-requisites
--------------

* Python3 & pip
* MariaDB

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

