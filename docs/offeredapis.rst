.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

============
Offered APIs
============
Etsicatalog provides the followed APIs:

-  **NS package management interface**

  Provides runtime NS package management interface

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/nsd/v1/ns_descriptors
     - POST
     - Create a new NS descriptor resource.
   * - /api/nsd/v1/ns_descriptors
     - GET
     - Query information about multiple NS descriptor resources.
   * - /api/nsd/v1/ns_descriptors/{{nsdInfoId}}
     - GET
     - Read information about an individual NS descriptor resource.
   * - /api/nsd/v1/ns_descriptors/{{nsdInfoId}}/nsd_content
     - PUT
     - Upload the content of a NSD.
   * - /api/nsd/v1/ns_descriptors/{{nsdInfoId}}/nsd_content
     - GET
     - Fetch the content of a NSD.
   * - /api/nsd/v1/ns_descriptors/{{nsdInfoId}}
     - DELETE
     - Delete an individual NS descriptor resource.
   * - /api/nsd/v1/pnf_descriptors
     - POST
     - Create a new PNF descriptor resource.
   * - /api/nsd/v1/pnf_descriptors
     - GET
     - Query information about multiple PNF descriptor resources.
   * - /api/nsd/v1/pnf_descriptors/{{pnfdInfoId}}
     - GET
     - Read an individual PNFD resource.
   * - /api/nsd/v1/pnf_descriptors/{{pnfdInfoId}}/pnfd_content
     - PUT
     - Upload the content of a PNFD.
   * - /api/nsd/v1/pnf_descriptors/{{pnfdInfoId}}/pnfd_content
     - GET
     - Fetch the content of a PNFD.
   * - /api/nsd/v1/pnf_descriptors/{{pnfdInfoId}}
     - DELETE
     - Delete an individual PNF descriptor resource.

-  **VNF package management interface**

  Provides runtime VNF package management interface

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/vnfpkgm/v1/vnf_packages
     - POST
     - Create a new individual VNF package resource
   * - /api/vnfpkgm/v1/vnf_packages
     - GET
     - Query VNF packages information
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}
     - GET
     - Read information about an individual VNF package
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}/package_content
     - PUT
     - Upload a VNF package by providing the content of the VNF package
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}/package_content/upload_from_uri
     - PUT
     - Upload a VNF package by providing the address information of the VNF package
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}/package_content
     - GET
     - Fetch an on-boarded VNF package
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}/vnfd
     - GET
     - Read VNFD of an on-boarded VNF package
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}/artifacts/{{artifactPath}}
     - GET
     - Fetch individual VNF package artifact
   * - /api/vnfpkgm/v1/vnf_packages/{{vnfPkgId}}
     - DELETE
     - Delete an individual VNF package
   * - /api/vnfpkgm/v1/subscriptions
     - POST
     - Subscribe to notifications related to on-boarding and/or changes of VNF packages
   * - /api/vnfpkgm/v1/subscriptions
     - GET
     - Query multiple subscriptions
   * - /api/vnfpkgm/v1/subscriptions/{{subscriptionId}}
     - GET
     - Read an individual subscription resource
   * - /api/vnfpkgm/v1/subscriptions/{{subscriptionId}}
     - DELETE
     - Terminate a subscription

-  **Catalog interface**

  Provides APIs to query/fetch package from SDC catalog

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/catalog/v1/nspackages
     - POST
     - Fetch NS package from SDC catalog
   * - /api/catalog/v1/vnfpackages
     - POST
     - Fetch NVF package from SDC catalog
   * - /api/catalog/v1/service_packages
     - POST
     - Fetch Service package from SDC catalog

-  **Parser interface**

  Provide APIs to parser VNF/PNF/NS/Service package

.. list-table::
   :widths: 50 10 40
   :header-rows: 1

   * - URL
     - Method
     - Description
   * - /api/parser/v1/parserpnfd
     - POST
     - Parse PNF package
   * - /api/parser/v1/parservnfd
     - POST
     - Parse VNF package
   * - /api/parser/v1/parsernsd
     - POST
     - Parse NS package
   * - /api/parser/v1/parser
     - POST
     - Parse package

You can download the following API yaml file and paste the content into the swagger tool: https://editor.swagger.io to view more detail of APIs.

:download:`etsicatalog_API_v1.yaml <swagger/etsicatalog_API_v1.yaml>`
