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
MSB_SERVICE_PROTOCOL = env_dict.get('MSB_PROTO', 'http')
MSB_SERVICE_IP = env_dict.get('MSB_ADDR', '127.0.0.1:80').split(':')[0]
MSB_SERVICE_PORT = env_dict.get('MSB_ADDR', '127.0.0.1:80').split(':')[1]
MSB_BASE_URL = "%s://%s:%s" % (MSB_SERVICE_PROTOCOL, MSB_SERVICE_IP, MSB_SERVICE_PORT)

# [mysql]
DB_IP = env_dict.get('MYSQL_ADDR', "127.0.0.1:3306").split(':')[0]
DB_PORT = env_dict.get('MYSQL_ADDR', "127.0.0.1:3306").split(':')[1]
DB_NAME = "etsicatalog"
DB_USER = "etsicatalog"
DB_PASSWD = "etsicatalog"

# [MDC]
SERVICE_NAME = "catalog"
FORWARDED_FOR_FIELDS = ["HTTP_X_FORWARDED_FOR", "HTTP_X_FORWARDED_HOST",
                        "HTTP_X_FORWARDED_SERVER"]

# [register]
REG_TO_MSB_WHEN_START = True
REG_TO_MSB_REG_URL = "/api/microservices/v1/services"
SSL_ENABLED = env_dict.get('SSL_ENABLED', "true")
if SSL_ENABLED == "true":
    enable_ssl = "true"
else:
    enable_ssl = "false"
svc_ip = env_dict.get('SERVICE_IP', '127.0.0.1')
REG_TO_MSB_REG_PARAM = [{
    "serviceName": "catalog",
    "version": "v1",
    "enable_ssl": enable_ssl,
    "url": "/api/catalog/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": svc_ip,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "nsd",
    "version": "v1",
    "enable_ssl": enable_ssl,
    "url": "/api/nsd/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": svc_ip,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "vnfpkgm",
    "version": "v1",
    "enable_ssl": enable_ssl,
    "url": "/api/vnfpkgm/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": svc_ip,
        "port": "8806",
        "ttl": 0
    }]
}, {
    "serviceName": "parser",
    "version": "v1",
    "enable_ssl": enable_ssl,
    "url": "/api/parser/v1",
    "protocol": "REST",
    "visualRange": "1",
    "nodes": [{
        "ip": svc_ip,
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

# [sdc config]
SDC_BASE_URL = MSB_BASE_URL + "/api"
SDC_USER = "modeling"
SDC_PASSWD = "Kp8bJ4SXszM0WXlhak3eHlcse2gAw84vaoGGmJvUy2U"

# [dmaap config]
DMAAP_MR_IP = MSB_SERVICE_IP
DMAAP_MR_PORT = '30226'
CONSUMER_GROUP = "consumerGroup"
CONSUMER_ID = "consumerId"
POLLING_INTERVAL = 15

VNFD_SCHEMA_VERSION_DEFAULT = "base"
