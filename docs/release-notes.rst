.. This work is licensed under a Creative
.. Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. _release_notes:


Release Notes
==============

etsicatalog provides package management service and parser service as Micro
Service.

Version: 1.0.12
--------------

:Release Date: 2022-03-18

**New Features**

- update Django version to 3.1.4
- Update the vulnerable direct dependencies

Released components:
 - etsicatalog 1.0.12


Version: 1.0.11
--------------

:Release Date: 2021-08-31

**New Features**

- update PyYAML & httplib2 version

Released components:
 - etsicatalog 1.0.11


Version: 1.0.10
---------------

:Release Date: 2021-03-03

**New Features**

- Support Subscription and Notification for NSD packages
- Refactor logging to remove dependency on onaplogging component
- Upgrade to Python3.8
- Update document of installation and developer guide

**Bug Fixes**

- Fix bug: Get VNF Package Artifact endpoint doesn't accept file extensions

Released components:
 - etsicatalog 1.0.10


Version: 1.0.9
--------------

:Release Date: 2020-11-03

**New Features**

- Support SDC-ETSI Catalog Manager direct interface
- Query SDC for ETSI packages from the ETSI_PACKAGE directory and store the packages
- Optimize the docker image
- Remove the mandatory dependency on MSB

Released components:
 - etsicatalog 1.0.9


Version: 1.0.6
--------------

:Release Date: 2020-05-11

**New Features**

- optimize the docker image

Released components:
 - etsicatalog 1.0.6

Version: 1.0.5
--------------

:Release Date: 2020-03-03

**New Features**

- VNF subscription and notification support
- Support ONBOARDING_PACKAGE directory to get original vendor package
- Unify API endpoint
- Add API to read VNFD

Released components:
 - etsicatalog 1.0.5

**Bug Fixes**

None

**Known Issues**

By now etsicatalog has not supported HTTPS directly. But all of APIs have registered to MSB and client can call etsicatalog APIs through MSB HTTPS request, such as: curl -X GET 'https://msb_ip:msb_port/api/vnfpkgm/v1/subscriptions'.

**Security Issues**

None

**Upgrade Notes**

Update API endpoint:

- Chang "api/parser/v1/service_packages" -> "api/catalog/v1/service_packages"
- Unify parser API as "api/parser/V1/..."

**Deprecation Notes**

None

**Other**

Version: 1.0.4
--------------

:Release Date: 2019-09-17

**New Features**

- Update to python3
- Optimize the process of service package distribution
- Merge with vfc/catalog


Released components:
 - etsicatalog 1.0.4

**Bug Fixes**

None

**Known Issues**

None

**Security Issues**

- `El Alto Vulnerability Report <https://wiki.onap.org/pages/viewpage.action?pageId=68541425>`_

**Upgrade Notes**

None

**Deprecation Notes**

None

**Other**

===========

Version: 1.0.2
--------------

:Release Date: 2019-06-06

**New Features**

- Package management service.
- Parser service.


Released components:
 - etsicatalog 1.0.2

**Bug Fixes**

This is the initial release

**Known Issues**

None

**Security Issues**

None

**Upgrade Notes**

This is the initial release

**Deprecation Notes**

This is the initial release

**Other**

===========

End of Release Notes
