.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

Installation
============

.. contents::
   :depth: 3
..

This document describes Modeling/etsicatalog installation by OOM.

OOM Charts
-----------

The Modeling/etsicatalog K8S charts are located in the OOM repository:
https://gerrit.onap.org/r/admin/repos/oom

For OOM deployment you can refer to the OOM documentation.


.. * https://docs.onap.org/projects/onap-oom/en/latest/oom_user_guide.html#oom-user-guide
.. * https://docs.onap.org/projects/onap-oom/en/latest/oom_quickstart_guide.html#oom-quickstart-guide


Installing or Upgrading
------------------------

The assumption is you have cloned the charts from the OOM repository into a local directory.

Step 1 Go into local copy of OOM charts

From your local copy, edit the values.yaml file to make desired changes.

Step 2 Build the chart
::

    $ cd oom/kubernetes
    $ make modeling
    $ helm search local|grep modeling

Step 3 Un-install if installed before
::

    $ helm delete  dev-modeling --purge
    $ kubectl -n onap get pod |grep modeling-mariadb

Step 4 Delete persistent volume claim and NFS persisted data for etsicatalog
::

    $ kubectl -n onap get pvc |grep dev-modeling|awk '{print $1}'|xargs kubectl -n onap delete pvc
    $ rm -rf /dockerdata-nfs/dev-modeling/

Step 5 Reinstall
::

    $ helm install local/modeling --namespace onap --name dev-modeling
    $ kubectl -n onap get pod |grep modeling


Etsicatalog Pods
-----------------

To get the etsicatalog Pod, run the following command:
::

    $ kubectl -n onap get pods | grep modeling

    dev-modeling-etsicatalog-754f4d6f94-lmjzz       2/2     Running                 2          92d

To access the etsicatalog docker container, run the command:
::

    $ kubectl -n onap exec -it dev-modeling-etsicatalog-754f4d6f94-lmjzz -c modeling-etsicatalog -- /bin/bash

To restart the pod, run the command:
::

    $ kubectl delete pod dev-modeling-etsicatalog-754f4d6f94-lmjzz -n onap

From Guilin Release, etsicatalog uses the public database:
::

   $ kubectl -n onap get pods | grep mariadb-galera

   dev-mariadb-galera-0                               2/2     Running            0          14d
   dev-mariadb-galera-1                               2/2     Running            0          14d
   dev-mariadb-galera-2                               2/2     Running            0          14d

Exposing ports
---------------

For security reasons, the port for the etsicatalog container is configured as ClusterIP and thus not exposed. If you need the port in a development environment, then the following command will expose it.
::

    $ kubectl -n onap expose service modeling-etsicatalog --target-port=8806 --type=NodePort





