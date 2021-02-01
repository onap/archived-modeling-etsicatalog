.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. _architecture:

============
Architecture
============

Introduction
------------

The Etsicatalog project provides a runtime catalog service which can be consumed by other projects or components, such as UUI, VF-C, etc.
The catalog can be used to store packages distributed by the SDC, and also includes a TOSCA parser service.

Etsicatalog is a web application based on python3 and Django framework. It is a standalone micro-service which provides:

- Package Management Service
- Parser Service

.. image:: images/architecture.png
