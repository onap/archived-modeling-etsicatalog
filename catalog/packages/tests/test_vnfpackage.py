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

import json
import mock
import os
import catalog.pub.utils.timeutil
from requests.auth import HTTPBasicAuth

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from catalog.packages.biz.sdc_vnf_package import NfDistributeThread, NfPkgDeleteThread
from catalog.pub.database.models import JobStatusModel, JobModel
from catalog.pub.database.models import VnfPackageModel
from catalog.pub.msapi import sdc
from catalog.pub.utils import restcall, toscaparser
from .const import vnfd_data
from catalog.pub.config.config import CATALOG_ROOT_PATH
from catalog.packages import const
from catalog.pub.config import config as pub_config


class TestNfPackage(TestCase):
    def setUp(self):
        self.client = APIClient()
        VnfPackageModel.objects.filter().delete()
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()
        self.vnfd_data = vnfd_data

    def tearDown(self):
        pass

    def assert_job_result(self, job_id, job_progress, job_detail):
        jobs = JobStatusModel.objects.filter(
            jobid=job_id,
            progress=job_progress,
            descp=job_detail)
        self.assertEqual(1, len(jobs))

    @mock.patch.object(NfDistributeThread, 'run')
    def test_nf_pkg_distribute_normal(self, mock_run):
        resp = self.client.post(
            "/api/catalog/v1/vnfpackages",
            {
                "csarId": "1",
                "vimIds": ["1"]
            },
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    def test_nf_pkg_distribute_when_csar_already_exist(self):
        VnfPackageModel(
            vnfPackageId="1",
            vnfdId="vcpe_vfw_zte_1_0"
        ).save()
        NfDistributeThread(
            csar_id="1",
            vim_ids=["1"],
            lab_vim_id="",
            job_id="2"
        ).run()
        self.assert_job_result("2", 255, "NF CSAR(1) already exists.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(sdc, 'download_artifacts')
    @mock.patch.object(toscaparser, 'parse_vnfd')
    def test_nf_pkg_distribute_when_vnfd_already_exist(self,
                                                       mock_parse_vnfd,
                                                       mock_download_artifacts,
                                                       mock_call_req):
        mock_parse_vnfd.return_value = json.JSONEncoder().encode(self.vnfd_data)
        mock_download_artifacts.return_value = "/home/hss.csar"
        mock_call_req.return_value = [0, json.JSONEncoder().encode([{
            "uuid": "1",
            "toscaModelURL": "https://127.0.0.1:1234/sdc/v1/hss.csar"
        }]), '200']
        VnfPackageModel(vnfPackageId="2", vnfdId="00342b18-a5c7-11e8-998c-bf1755941f12").save()
        NfDistributeThread(
            csar_id="1",
            vim_ids=["1"],
            lab_vim_id="",
            job_id="2"
        ).run()
        self.assert_job_result("2", 255, "VNF package(00342b18-a5c7-11e8-998c-bf1755941f12) already exists.")

    @mock.patch.object(restcall, 'call_req')
    @mock.patch.object(sdc, 'download_artifacts')
    @mock.patch.object(toscaparser, 'parse_vnfd')
    def test_nf_pkg_distribute_successfully(self,
                                            mock_parse_vnfd,
                                            mock_download_artifacts,
                                            mock_call_req):
        mock_parse_vnfd.return_value = json.JSONEncoder().encode(self.vnfd_data)
        mock_download_artifacts.return_value = "/home/hss.csar"
        mock_call_req.return_value = [0, json.JSONEncoder().encode([{
            "uuid": "1",
            "toscaModelURL": "https://127.0.0.1:1234/sdc/v1/hss.csar"
        }]), '200']
        NfDistributeThread(
            csar_id="1",
            vim_ids=["1"],
            lab_vim_id="",
            job_id="4"
        ).run()
        self.assert_job_result("4", 100, "CSAR(1) distribute successfully.")

    ###############################################################################################################

    @mock.patch.object(NfPkgDeleteThread, 'run')
    def test_nf_pkg_delete_normal(self, mock_run):
        resp = self.client.delete("/api/catalog/v1/vnfpackages/1")
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)

    def test_nf_pkg_normal_delete(self):
        VnfPackageModel(
            vnfPackageId="2",
            vnfdId="vcpe_vfw_zte_1_0"
        ).save()
        NfPkgDeleteThread(
            csar_id="2",
            job_id="2"
        ).run()
        self.assert_job_result("2", 100, "Delete CSAR(2) successfully.")

    def test_nf_pkg_get_all(self):
        VnfPackageModel(
            vnfPackageId="3",
            vnfdId="3",
            vnfVendor='3',
            vnfdVersion='3',
            vnfSoftwareVersion='',
            vnfPackageUri='',
            vnfdModel=''
        ).save()
        VnfPackageModel(
            vnfPackageId="4",
            vnfdId="4",
            vnfVendor='4',
            vnfdVersion='4',
            vnfSoftwareVersion='',
            vnfPackageUri='',
            vnfdModel=''
        ).save()
        resp = self.client.get("/api/catalog/v1/vnfpackages")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expect_data = [
            {
                "imageInfo": [],
                "csarId": "3",
                "packageInfo": {
                    "csarName": "",
                    "vnfdModel": "",
                    "vnfdProvider": "3",
                    "vnfdId": "3",
                    "downloadUrl": "http://127.0.0.1:8806/static/catalog/3/",
                    "vnfVersion": "",
                    "vnfdVersion": "3",
                    "vnfPackageId": "3"
                }
            },
            {
                "imageInfo": [],
                "csarId": "4",
                "packageInfo": {
                    "csarName": "",
                    "vnfdModel": "",
                    "vnfdProvider": "4",
                    "vnfdId": "4",
                    "downloadUrl": "http://127.0.0.1:8806/static/catalog/4/",
                    "vnfVersion": "",
                    "vnfdVersion": "4",
                    "vnfPackageId": "4"
                }
            }
        ]
        self.assertEqual(expect_data, resp.data)

    def test_nf_pkg_get_one(self):
        VnfPackageModel(
            vnfPackageId="4",
            vnfdId="4",
            vnfVendor='4',
            vnfdVersion='4',
            vnfSoftwareVersion='',
            vnfPackageUri='',
            vnfdModel=''
        ).save()

        resp = self.client.get("/api/catalog/v1/vnfpackages/4")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        expect_data = {
            "imageInfo": [],
            "csarId": "4",
            "packageInfo": {
                "csarName": "",
                "vnfdModel": "",
                "vnfdProvider": "4",
                "vnfdId": "4",
                "downloadUrl": "http://127.0.0.1:8806/static/catalog/4/",
                "vnfVersion": "",
                "vnfdVersion": "4",
                "vnfPackageId": "4"
            }
        }
        self.assertEqual(expect_data, resp.data)

    def test_nf_pkg_get_one_failed(self):
        VnfPackageModel(
            vnfPackageId="4",
            vnfdId="4",
            vnfVendor='4',
            vnfdVersion='4',
            vnfSoftwareVersion='',
            vnfPackageUri='',
            vnfdModel=''
        ).save()

        resp = self.client.get("/api/catalog/v1/vnfpackages/2")
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual({'error': 'Vnf package[2] not Found.'}, resp.data)

    ###############################################################################################################

    @mock.patch.object(toscaparser, 'parse_vnfd')
    def test_vnfd_parse_normal(self, mock_parse_vnfd):
        VnfPackageModel(
            vnfPackageId="8",
            vnfdId="10"
        ).save()
        mock_parse_vnfd.return_value = json.JSONEncoder().encode({"c": "d"})
        req_data = {
            "csarId": "8",
            "inputs": []
        }
        resp = self.client.post(
            "/api/parser/v1/parservnfd",
            req_data,
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual({"model": '{"c": "d"}'}, resp.data)

    def test_vnfd_parse_when_csar_not_exist(self):
        req_data = {"csarId": "1", "inputs": []}
        resp = self.client.post(
            "/api/parser/v1/parservnfd",
            req_data,
            format='json'
        )
        self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(resp.data, {"error": "VNF CSAR(1) does not exist."})

    @mock.patch("requests.post")
    @mock.patch.object(sdc, 'download_artifacts')
    @mock.patch.object(sdc, 'get_artifact')
    @mock.patch("requests.get")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_service_pkg_distribute_and_notify(self, mock_nowtime, mock_uuid, mock_requests_get, mock_get_artifact,
                                               mock_download_artifacts, mock_requests_post):
        mock_nowtime.return_value = "2019-02-16 14:41:16"
        uuid_subscriptid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        uuid_csarid = "1234"
        mock_uuid.side_effect = [uuid_subscriptid, "1111", "2222"]
        mock_requests_get.return_value.status_code = 204
        vnf_subscription_data = {
            "filter": {
                "notificationTypes": [
                    "VnfPackageOnboardingNotification",
                    "VnfPackageChangeNotification"
                ],
                "vnfPkgId": [uuid_csarid],
                "operationalState": ["ENABLED", "DISABLED"]
            },
            "callbackUri": "https://so-vnfm-simulator.onap:9093/vnfpkgm/v1/notification",
            "authentication": {
                "authType": [
                    "BASIC"
                ],
                "paramsBasic": {
                    "userName": "vnfm",
                    "password": "password1$"
                }
            }
        }
        response = self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=vnf_subscription_data,
            format='json')
        self.assertEqual(201, response.status_code)
        mock_download_artifacts.return_value = os.path.join(CATALOG_ROOT_PATH, "Sol004VnfCSAR.csar")
        mock_get_artifact.return_value = {
            "uuid": "c94490a0-f7ef-48be-b3f8-8d8662a37236",
            "invariantUUID": "63eaec39-ffbe-411c-a838-448f2c73f7eb",
            "name": "Sol004VnfCSAR",
            "version": "2.0",
            "toscaModelURL": "/sdc/v1/catalog/resources/c94490a0-f7ef-48be-b3f8-8d8662a37236/toscaModel",
            "category": "Volte",
            "subCategory": "VolteVF",
            "resourceType": "VF",
            "lifecycleState": "CERTIFIED",
            "lastUpdaterUserId": "jh0003"
        }
        NfDistributeThread(csar_id=uuid_csarid, vim_ids=["1"], lab_vim_id="", job_id="4").on_distribute()
        print(VnfPackageModel.objects.all().values())
        expect_onboarding_notification = {
            'id': "1111",
            'notificationType': const.PKG_NOTIFICATION_TYPE.ONBOARDING,
            'timeStamp': "2019-02-16 14:41:16",
            'vnfPkgId': "1234",
            'vnfdId': "b1bb0ce7-2222-4fa7-95ed-4840d70a1177",
            '_links': {
                'vnfPackage': {
                    'href': '%s/%s/vnf_packages/%s' % (pub_config.MSB_BASE_URL,
                                                                 const.PKG_URL_PREFIX,
                                                                 uuid_csarid)},
                'subscription': {
                    'href': '%s/%s%s' % (pub_config.MSB_BASE_URL,
                                                   const.VNFPKG_SUBSCRIPTION_ROOT_URI,
                                                   uuid_subscriptid)}

            },
            "subscriptionId": uuid_subscriptid
        }
        mock_requests_post.return_value.status_code = 204
        mock_requests_post.assert_called_with(vnf_subscription_data["callbackUri"],
                                              data=json.dumps(expect_onboarding_notification),
                                              headers={'Connection': 'close',
                                                       'content-type': 'application/json',
                                                       'accept': 'application/json'},
                                              auth=HTTPBasicAuth("vnfm", "password1$"),
                                              verify=False)
        mock_requests_post.return_value.status_code = 204
        expect_deleted_notification = {
            'id': "2222",
            'notificationType': const.PKG_NOTIFICATION_TYPE.CHANGE,
            'timeStamp': "2019-02-16 14:41:16",
            'vnfPkgId': "1234",
            'vnfdId': "b1bb0ce7-2222-4fa7-95ed-4840d70a1177",
            '_links': {
                'vnfPackage': {
                    'href': '%s/%s/vnf_packages/%s' % (pub_config.MSB_BASE_URL,
                                                                 const.PKG_URL_PREFIX,
                                                                 uuid_csarid)},
                    'subscription': {
                        'href': '%s/%s%s' % (pub_config.MSB_BASE_URL,
                                                       const.VNFPKG_SUBSCRIPTION_ROOT_URI,
                                                       uuid_subscriptid)}

            },
            'changeType': const.PKG_CHANGE_TYPE.PKG_DELETE,
            'operationalState': None,
            "subscriptionId": uuid_subscriptid
        }
        NfPkgDeleteThread(csar_id=uuid_csarid, job_id="5").delete_csar()
        mock_requests_post.assert_called_with(vnf_subscription_data["callbackUri"],
                                              data=json.dumps(expect_deleted_notification),
                                              headers={'Connection': 'close',
                                                       'content-type': 'application/json',
                                                       'accept': 'application/json'},
                                              auth=HTTPBasicAuth("vnfm", "password1$"),
                                              verify=False)
