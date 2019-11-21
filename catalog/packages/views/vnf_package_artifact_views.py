# Copyright (C) 2019 Verizon. All Rights Reserved
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

import logging

from django.http import FileResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView

from catalog.packages.biz.vnf_pkg_artifacts import FetchVnfPkgArtifact
from catalog.packages.const import TAG_VNF_PACKAGE_API
from .common import view_safe_call_with_log

logger = logging.getLogger(__name__)

VALID_FILTERS = [
    "callbackUri",
    "notificationTypes",
    "vnfdId",
    "vnfPkgId",
    "operationalState",
    "usageState"
]


class FetchVnfPkgmArtifactsView(APIView):

    @swagger_auto_schema(
        tags=[TAG_VNF_PACKAGE_API],
        responses={
            status.HTTP_200_OK: "Return the artifact file",
            status.HTTP_404_NOT_FOUND: "Artifact not found",
            status.HTTP_500_INTERNAL_SERVER_ERROR: "Internal error"
        }
    )
    @view_safe_call_with_log(logger=logger)
    def get(self, request, vnfPkgId, artifactPath):
        logger.debug("FetchVnfPkgmArtifactsView--get::> ")

        resp_data = FetchVnfPkgArtifact().fetch(vnfPkgId, artifactPath)
        response = FileResponse(resp_data)

        return response
