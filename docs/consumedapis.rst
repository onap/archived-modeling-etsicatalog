.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

=============
Consumed APIs
=============

SDC
---
Etsicatalog invokes SDC APIs to query/fetch package from SDC catalog.

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/sdc/v1/catalog/services/
     - GET
     - Get service list
   * - /api/sdc/v1/catalog/services/{{csarId}}/metadata
     - GET
     - Get a service metadata
   * - /api/sdc/v1/catalog/resources
     - GET
     - Get resource list
   * - /api/sdc/v1/catalog/resources/{{csarId}}/metadata
     - GET
     - Get a resource metadata
   * - /api/sdc/v1/catalog/services/{{csarId}}/toscaModel
     - GET
     - Download a service package

Micro Service Bus
-----------------
Etsicatalog invokes Micro Service Bus APIs to register service to MSB.

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/microservices/v1/services
     - POST
     - Register service to the Microservice Bus