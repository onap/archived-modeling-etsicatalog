# Copyright 2017 ZTE Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

# [MSB]
MSB_BASE_URL = os.getenv("MSB_ADDR", "http://127.0.0.1:80")
MSB_ENABLED = os.getenv("MSB_ENABLED", "false")

# [SDC config]
if MSB_ENABLED == "true":
    SDC_BASE_URL = MSB_BASE_URL + "/api"
else:
    SDC_BASE_URL = os.getenv("SDC_ADDR")
SDC_USER = "modeling"
SDC_PASSWD = "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"

SERVICE_IP = os.getenv("SERVICE_IP", "127.0.0.1")

# [DMAAP config]
DMAAP_ENABLED = os.getenv("DMAAP_ENABLED", "false")
DMAAP_MR_BASE_URL = os.getenv("DMAAP_ADDR")
CONSUMER_GROUP = "consumerGroup"
CONSUMER_ID = "consumerId"
POLLING_INTERVAL = 15

# [mysql]
DB_IP = os.getenv("DB_IP", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = "etsicatalog"
DB_USER = os.getenv("DB_USER", "etsicatalog")
DB_PASSWD = os.getenv("DB_PASSWD", "etsicatalog")

# [MDC]
SERVICE_NAME = "catalog"
FORWARDED_FOR_FIELDS = ["HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_HOST",
                        "HTTP_X_FORWARDED_SERVER"]

# [register]
REG_TO_MSB_WHEN_START = False
REG_TO_MSB_REG_URL = "/api/microservices/v1/services"
SSL_ENABLED = os.getenv("SSL_ENABLED", "false")
REG_TO_MSB_REG_PARAM = [{
    "serviceName": "catalog",
    "version": "v1",
    "enable_ssl": SSL_ENABLED,
    "url": "/api/catalog/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": SERVICE_IP,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "nsd",
    "version": "v1",
    "enable_ssl": SSL_ENABLED,
    "url": "/api/nsd/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": SERVICE_IP,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "vnfpkgm",
    "version": "v1",
    "enable_ssl": SSL_ENABLED,
    "url": "/api/vnfpkgm/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": SERVICE_IP,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "parser",
    "version": "v1",
    "enable_ssl": SSL_ENABLED,
    "url": "/api/parser/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": SERVICE_IP,
        "port": "8806",
        "ttl": 0
    }]
}]
MSB_SVC_CALALOG_URL = "/api/microservices/v1/services/catalog/version/v1"
MSB_SVC_NSD_URL = "/api/microservices/v1/services/nsd/version/v1"
MSB_SVC_VNFPKGM_URL = "/api/microservices/v1/services/vnfpkgm/version/v1"
MSB_SVC_PARSER_URL = "/api/microservices/v1/services/parser/version/v1"

# catalog path(values is defined in settings.py)
CATALOG_ROOT_PATH = None
CATALOG_URL_PATH = None

VNFD_SCHEMA_VERSION_DEFAULT = "base"
