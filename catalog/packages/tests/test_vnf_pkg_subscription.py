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

import uuid
import mock
import json
import os

from rest_framework.test import APIClient
from django.test import TestCase

from catalog.pub.database.models import VnfPkgSubscriptionModel, VnfPackageModel
from .const import vnf_subscription_data, vnfd_data
from catalog.packages.biz.notificationsutil import NotificationsUtil, prepare_vnfpkg_notification
from catalog.packages import const
from catalog.pub.config import config as pub_config
import catalog.pub.utils.timeutil
from catalog.pub.utils import toscaparser
from catalog.pub.config.config import CATALOG_ROOT_PATH
from rest_framework import status


class TestNfPackageSubscription(TestCase):
    def setUp(self):
        self.client = APIClient()
        VnfPkgSubscriptionModel.objects.filter().delete()
        self.vnf_subscription_data = vnf_subscription_data

    def tearDown(self):
        pass

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_create_vnf_subscription(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            self.vnf_subscription_data["callbackUri"],
            response.data["callbackUri"]
        )
        self.assertEqual(temp_uuid, response.data["id"])

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_duplicate_subscriptions(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        temp1_uuid = "00342b18-a5c7-11e8-998c-bf1755941f12"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.side_effect = [temp_uuid, temp1_uuid]
        response = self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            self.vnf_subscription_data["callbackUri"],
            response.data["callbackUri"]
        )
        self.assertEqual(temp_uuid, response.data["id"])
        temp_uuid = "00442b18-a5c7-11e8-998c-bf1755941f12"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        self.assertEqual(303, response.status_code)

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_get_subscriptions(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        response = self.client.get(
            "/api/vnfpkgm/v1/subscriptions?usageState=IN_USE",
            format='json'
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_get_subscriptions_with_invalid_params(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        response = self.client.get(
            "/api/vnfpkgm/v1/subscriptions?dummy=dummy",
            format='json'
        )
        self.assertEqual(400, response.status_code)

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_get_subscription_with_id(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        response = self.client.get(
            "/api/vnfpkgm/v1/subscriptions/%s" % temp_uuid,
            format='json'
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(temp_uuid, response.data["id"])

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_get_subscription_with_id_not_exists(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        dummy_uuid = str(uuid.uuid4())
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        response = self.client.get(
            "/api/vnfpkgm/v1/subscriptions/%s" % dummy_uuid,
            format='json'
        )
        self.assertEqual(404, response.status_code)

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_delete_subscription_with_id(self, mock_uuid4, mock_requests):
        temp_uuid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        dummy_uuid = str(uuid.uuid4())
        mock_requests.return_value.status_code = 204
        mock_requests.get.status_code = 204
        mock_uuid4.return_value = temp_uuid
        self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=self.vnf_subscription_data,
            format='json'
        )
        self.client.get(
            "/api/vnfpkgm/v1/subscriptions/%s" % dummy_uuid,
            format='json'
        )
        response = self.client.delete("/api/vnfpkgm/v1/subscriptions/%s" % temp_uuid)
        self.assertEqual(204, response.status_code)

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_delete_subscription_with_id_not_exists(self, mock_uuid4, mock_requests):
        dummy_uuid = str(uuid.uuid4())
        response = self.client.delete("/api/vnfpkgm/v1/subscriptions/%s" % dummy_uuid)
        self.assertEqual(404, response.status_code)

    @mock.patch("requests.get")
    @mock.patch.object(toscaparser, 'parse_vnfd')
    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_vnfpkg_subscript_notify(self, mock_nowtime, mock_uuid, mock_requests_post, mock_parse_vnfd, mock_requests_get):
        mock_nowtime.return_value = "nowtime()"
        uuid_subscriptid = "99442b18-a5c7-11e8-998c-bf1755941f13"
        uuid_vnfPackageId = "3fa85f64-5717-4562-b3fc-2c963f66afa6"
        uuid_vnfdid = "00342b18-a5c7-11e8-998c-bf1755941f12"
        mock_uuid.side_effect = [uuid_subscriptid, "1111"]
        mock_requests_get.return_value.status_code = 204
        mock_parse_vnfd.return_value = json.JSONEncoder().encode(vnfd_data)

        response = self.client.post(
            "/api/vnfpkgm/v1/subscriptions",
            data=vnf_subscription_data,
            format='json')
        self.assertEqual(201, response.status_code)

        data = {'file': open(os.path.join(CATALOG_ROOT_PATH, "empty.txt"), "rt")}
        VnfPackageModel.objects.create(
            vnfPackageId=uuid_vnfPackageId,
            onboardingState="CREATED"
        )

        response = self.client.put("/api/vnfpkgm/v1/vnf_packages/%s/package_content" % uuid_vnfPackageId, data=data)
        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=uuid_vnfPackageId)
        self.assertEqual(uuid_vnfdid, vnf_pkg[0].vnfdId)
        self.assertEqual(const.PKG_STATUS.ONBOARDED, vnf_pkg[0].onboardingState)
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        expect_notification = {
            'id': "1111",
            'notificationType': const.PKG_NOTIFICATION_TYPE.ONBOARDING,
            'timeStamp': "nowtime()",
            'vnfPkgId': uuid_vnfPackageId,
            'vnfdId': uuid_vnfdid,
            'changeType': const.PKG_CHANGE_TYPE.OP_STATE_CHANGE,
            'operationalState': None,
            "subscriptionId": uuid_subscriptid,
            '_links': {
                'subscription': {
                    'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                                   pub_config.MSB_SERVICE_PORT,
                                                   const.VNFPKG_SUBSCRIPTION_ROOT_URI,
                                                   uuid_subscriptid)},
                'vnfPackage': {
                    'href': 'http://%s:%s/%s/vnf_packages/%s' % (pub_config.MSB_SERVICE_IP,
                                                                 pub_config.MSB_SERVICE_PORT,
                                                                 const.PKG_URL_PREFIX,
                                                                 uuid_vnfPackageId)
                }
            }
        }
        mock_requests_post.assert_called_with(vnf_subscription_data["callbackUri"], data=expect_notification,
                                              headers={'Connection': 'close'})


class NotificationTest(TestCase):
    def setUp(self):
        VnfPackageModel.objects.all().delete()
        VnfPkgSubscriptionModel.objects.all().delete()

    def tearDown(self):
        VnfPackageModel.objects.all().delete()
        VnfPkgSubscriptionModel.objects.all().delete()

    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_vnfpkg_manual_notify(self, mock_nowtime, mock_uuid, mock_requests_post):
        VnfPackageModel(vnfPackageId="vnfpkgid1",
                        vnfdId="vnfdid1"
                        ).save()

        VnfPkgSubscriptionModel(subscription_id="1",
                                callback_uri="http://127.0.0.1/self",
                                notification_types=const.NOTIFICATION_TYPES,
                                vnfd_id="vnfdid1",
                                vnf_pkg_id="vnfpkgid1"
                                ).save()
        mock_nowtime.return_value = "nowtime()"
        mock_uuid.return_value = "1111"
        notification_content = prepare_vnfpkg_notification("vnfpkgid1", const.PKG_NOTIFICATION_TYPE.CHANGE,
                                                           const.PKG_CHANGE_TYPE.OP_STATE_CHANGE, operational_state=None)
        filters = {
            'vnfdId': 'vnfd_id',
            'vnfPkgId': 'vnf_pkg_id'
        }
        NotificationsUtil().send_notification(notification_content, filters, True)
        expect_callbackuri = "http://127.0.0.1/self"
        expect_notification = {
            'id': "1111",
            'notificationType': const.PKG_NOTIFICATION_TYPE.CHANGE,
            'timeStamp': "nowtime()",
            'vnfPkgId': "vnfpkgid1",
            'vnfdId': "vnfdid1",
            'changeType': const.PKG_CHANGE_TYPE.OP_STATE_CHANGE,
            'operationalState': None,
            "subscriptionId": "1",
            '_links': {
                'subscription': {
                    'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                                   pub_config.MSB_SERVICE_PORT,
                                                   const.VNFPKG_SUBSCRIPTION_ROOT_URI,
                                                   "1")},
                'vnfPackage': {
                    'href': 'http://%s:%s/%s/vnf_packages/%s' % (pub_config.MSB_SERVICE_IP,
                                                                 pub_config.MSB_SERVICE_PORT,
                                                                 const.PKG_URL_PREFIX,
                                                                 "vnfpkgid1")
                }
            }
        }
        mock_requests_post.assert_called_with(expect_callbackuri, data=expect_notification, headers={'Connection': 'close'})
