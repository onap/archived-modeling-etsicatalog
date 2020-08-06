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

env_dict = os.environ

# [MSB]
MSB_BASE_URL = env_dict.get("MSB_HOST", "http://127.0.0.1:80")
MSB_ENABLED = env_dict.get("MSB_ENABLED", True)

# [SDC config]
if MSB_ENABLED:
    SDC_BASE_URL = MSB_BASE_URL + "/api"
else:
    SDC_BASE_URL = env_dict.get("SDC_HOST")
SDC_USER = "modeling"
SDC_PASSWD = "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"

SERVICE_IP = env_dict.get("SERVICE_IP", "127.0.0.1")
SSL_ENABLED = env_dict.get("SSL_ENABLED", "false")

# [DMAAP config]
DMAAP_ENABLED = env_dict.get("DMAAP_ENABLED", False)
DMAAP_MR_BASE_URL = env_dict.get("DMAAP_HOST")
CONSUMER_GROUP = "consumerGroup"
CONSUMER_ID = "consumerId"
POLLING_INTERVAL = 15

# [mysql]
DB_IP = env_dict.get("MYSQL_ADDR", "127.0.0.1:3306").split(':')[0]
DB_PORT = env_dict.get("MYSQL_ADDR", "127.0.0.1:3306").split(':')[1]
DB_NAME = "etsicatalog"
DB_USER = "etsicatalog"
DB_PASSWD = "etsicatalog"

# [MDC]
SERVICE_NAME = "catalog"
FORWARDED_FOR_FIELDS = ["HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_HOST",
                        "HTTP_X_FORWARDED_SERVER"]

# [register]
REG_TO_MSB_WHEN_START = False
REG_TO_MSB_REG_URL = "/api/microservices/v1/services"
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
