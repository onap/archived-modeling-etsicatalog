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

import json
import mock
import uuid
import os
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from requests.auth import HTTPBasicAuth

from catalog.packages.biz.nsdm_subscription import NsdmSubscription
from catalog.pub.database.models import NsdmSubscriptionModel
from catalog.packages.biz.notificationsutil import NsdNotifications, PnfNotifications
from catalog.packages import const
from catalog.pub.config import config as pub_config
import catalog.pub.utils.timeutil
from catalog.packages.tests.const import nsd_data
from catalog.pub.database.models import NSPackageModel, VnfPackageModel, PnfPackageModel
from catalog.pub.config.config import CATALOG_ROOT_PATH
from catalog.pub.utils import toscaparser


class TestNsdmSubscription(TestCase):

    def setUp(self):
        self.client = APIClient()
        NsdmSubscriptionModel.objects.all().delete()
        self.subscription_id = str(uuid.uuid4())
        self.subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "nsdId": ["b632bddc-abcd-4180-bd8d-4e8a9578eff7"],
            }
        }
        self.links = {
            "self": {
                "href": "/api/v1/subscriptions/" + self.subscription_id
            }
        }
        self.test_subscription = {
            "callbackUri": "http://callbackuri.com",
            "id": self.subscription_id,
            "filter": {
                "notificationTypes": [
                    "NsdOnBoardingNotification"
                ],
                "nsdInfoId": [],
                "nsdId": [],
                "nsdName": [],
                "nsdVersion": [],
                "nsdInvariantId": [],
                "vnfPkgIds": [],
                "nestedNsdInfoIds": [],
                "nsdOnboardingState": [],
                "nsdOperationalState": [],
                "nsdUsageState": [],
                "pnfdInfoIds": [],
                "pnfdId": [],
                "pnfdName": [],
                "pnfdVersion": [],
                "pnfdProvider": [],
                "pnfdInvariantId": [],
                "pnfdOnboardingState": [],
                "pnfdUsageState": []
            },
            "_links": self.links,
        }

    def tearDown(self):
        pass

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_nsdm_subscribe_notification(self, mock_uuid4, mock_requests):
        temp_uuid = str(uuid.uuid4())
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        mock_uuid4.return_value = temp_uuid
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=self.subscription, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.subscription["callbackUri"],
                         response.data["callbackUri"])
        self.assertEqual(temp_uuid, response.data["id"])

    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_nsdm_subscribe_callbackFailure(self, mock_uuid4, mock_requests):
        temp_uuid = str(uuid.uuid4())
        mock_requests.return_value.status_code = 500
        mock_requests.get.return_value.status_code = 500
        mock_uuid4.return_value = temp_uuid
        expected_data = {
            'status': 500,
            'detail': "callbackUri http://callbackuri.com didn't"
                      " return 204 statuscode."
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=self.subscription, format='json')
        self.assertEqual(500, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_second_subscription(self, mock_requests):
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=self.subscription, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.subscription["callbackUri"],
                         response.data["callbackUri"])
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "nsdId": ["b632bddc-bccd-4180-bd8d-4e8a9578eff7"],
            }
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(dummy_subscription["callbackUri"],
                         response.data["callbackUri"])

    @mock.patch("requests.get")
    def test_nsdm_duplicate_subscription(self, mock_requests):
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=self.subscription, format='json')
        self.assertEqual(201, response.status_code)
        self.assertEqual(self.subscription["callbackUri"],
                         response.data["callbackUri"])
        expected_data = {
            'status': 303,
            'detail': 'Subscription has already existed with'
                      ' the same callbackUri and filter'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=self.subscription, format='json')
        self.assertEqual(303, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_bad_request(self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "nsdId": "b632bddc-bccd-4180-bd8d-4e8a9578eff7",
            }
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)

    @mock.patch("requests.get")
    def test_nsdm_invalid_authtype_subscription(self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["OAUTH2_CLIENT_CREDENTIALS"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'Auth type should be BASIC'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_invalid_authtype_oauthclient_subscription(
            self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsOauth2ClientCredentials": {
                    "clientId": "clientId",
                    "clientPassword": "password",
                    "tokenEndpoint": "http://tokenEndpoint"
                }
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'Auth type should be OAUTH2_CLIENT_CREDENTIALS'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_invalid_authparams_subscription(self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username"
                }
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'userName and password needed for BASIC'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_invalid_authparams_oauthclient_subscription(
            self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["OAUTH2_CLIENT_CREDENTIALS"],
                "paramsOauth2ClientCredentials": {
                    "clientPassword": "password",
                    "tokenEndpoint": "http://tokenEndpoint"
                }
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'clientId, clientPassword and tokenEndpoint'
                      ' required for OAUTH2_CLIENT_CREDENTIALS'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_invalid_filter_subscription(self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "nsdId": ["b632bddc-bccd-4180-bd8d-4e8a9578eff7"],
                "nsdInfoId": ["d0ea5ec3-0b98-438a-9bea-488230cff174"]
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'Notification Filter should contain'
                      ' either nsdId or nsdInfoId'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch("requests.get")
    def test_nsdm_invalid_filter_pnfd_subscription(self, mock_requests):
        dummy_subscription = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "pnfdId": ["b632bddc-bccd-4180-bd8d-4e8a9578eff7"],
                "pnfdInfoIds": ["d0ea5ec3-0b98-438a-9bea-488230cff174"]
            }
        }
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        expected_data = {
            'status': 400,
            'detail': 'Notification Filter should contain'
                      ' either pnfdId or pnfdInfoIds'
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=dummy_subscription, format='json')
        self.assertEqual(400, response.status_code)
        self.assertEqual(expected_data, response.data)

    @mock.patch.object(NsdmSubscription, 'create')
    def test_nsdmsubscription_create_when_catch_exception(self, mock_create):
        mock_create.side_effect = TypeError("Unicode type")
        response = self.client.post('/api/nsd/v1/subscriptions',
                                    data=self.subscription, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_nsdm_get_subscriptions(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.get("/api/nsd/v1/subscriptions",
                                   format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([self.test_subscription], response.data)

    def test_nsdm_get_subscriptions_filter(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.get("/api/nsd/v1/subscriptions"
                                   "?notificationTypes"
                                   "=NsdOnBoardingNotification",
                                   format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual([self.test_subscription], response.data)

    def test_nsdm_get_subscriptions_filter_failure(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.get("/api/nsd/v1/subscriptions"
                                   "?notificationTypes="
                                   "PnfdOnBoardingFailureNotification",
                                   format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_nsdm_get_subscriptions_invalid_filter(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.get("/api/nsd/v1/subscriptions"
                                   "?notificationTypes="
                                   "PnfdOnBoardingFailureNotificati",
                                   format='json')
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @mock.patch.object(NsdmSubscription, 'query_multi_subscriptions')
    def test_nsdmsubscription_get_when_catch_exception(self, mock_create):
        mock_create.side_effect = TypeError("Unicode type")
        response = self.client.get('/api/nsd/v1/subscriptions', format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_nsdm_get_subscription(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.get('/api/nsd/v1/'
                                   'subscriptions/' + self.subscription_id,
                                   format='json')
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(self.test_subscription, response.data)

    def test_nsdm_get_subscription_failure(self):
        expected_data = {
            "status": 404,
            "detail": "Subscription(" + self.subscription_id + ") "
            "doesn't exist"
        }
        response = self.client.get('/api/nsd/v1/'
                                   'subscriptions/' + self.subscription_id,
                                   format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)
        self.assertEqual(expected_data, response.data)

    def test_nsdm_get_subscription_failure_bad_request(self):
        response = self.client.get("/api/nsd/v1/subscriptions/123",
                                   format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @mock.patch.object(NsdmSubscription, 'query_single_subscription')
    def test_nsdmsubscription_getsingle_when_catch_exception(
            self, mock_create):
        mock_create.side_effect = TypeError("Unicode type")
        response = self.client.get('/api/nsd/v1/'
                                   'subscriptions/' + self.subscription_id,
                                   format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_ndsm_delete_subscription(self):
        NsdmSubscriptionModel(subscriptionid=self.subscription_id,
                              callback_uri="http://callbackuri.com",
                              auth_info={},
                              notificationTypes=json.dumps(
                                  ["NsdOnBoardingNotification"]),
                              nsdId=[], nsdVersion=[],
                              nsdInfoId=[], nsdDesigner=[],
                              nsdName=[], nsdInvariantId=[],
                              vnfPkgIds=[], pnfdInfoIds=[],
                              nestedNsdInfoIds=[], nsdOnboardingState=[],
                              nsdOperationalState=[], nsdUsageState=[],
                              pnfdId=[], pnfdVersion=[], pnfdProvider=[],
                              pnfdName=[], pnfdInvariantId=[],
                              pnfdOnboardingState=[], pnfdUsageState=[],
                              links=json.dumps(self.links)).save()
        response = self.client.delete('/api/nsd/v1/'
                                      'subscriptions/' + self.subscription_id,
                                      format='json')
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

    def test_ndsm_delete_subscription_failure(self):
        response = self.client.delete('/api/nsd/v1/'
                                      'subscriptions/' + self.subscription_id,
                                      format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    def test_nsdm_delete_subscription_failure_bad_request(self):
        response = self.client.delete("/api/nsd/v1/subscriptions/123",
                                      format='json')
        self.assertEqual(status.HTTP_404_NOT_FOUND, response.status_code)

    @mock.patch.object(NsdmSubscription, 'delete_single_subscription')
    def test_nsdmsubscription_delete_when_catch_exception(self, mock_create):
        mock_create.side_effect = TypeError("Unicode type")
        response = self.client.delete('/api/nsd/v1/'
                                      'subscriptions/' + self.subscription_id,
                                      format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_500_INTERNAL_SERVER_ERROR)

    @mock.patch("requests.post")
    @mock.patch.object(toscaparser, 'parse_nsd')
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    @mock.patch("requests.get")
    @mock.patch.object(uuid, 'uuid4')
    def test_nsdm_subscribe_trigger_notification(self, mock_uuid4, mock_requests, mock_nowtime, mock_parse_nsd,
                                                 mock_requests_post):
        mock_requests.return_value.status_code = 204
        mock_requests.get.return_value.status_code = 204
        mock_uuid4.return_value = "1111"
        mock_nowtime.return_value = "nowtime()"

        subscription_req = {
            "callbackUri": "http://callbackuri.com",
            "authentication": {
                "authType": ["BASIC"],
                "paramsBasic": {
                    "userName": "username",
                    "password": "password"
                }
            },
            "filter": {
                "nsdId": ["b632bddc-bccd-4180-bd8d-4e8a9578eff7"]
            }
        }
        response = self.client.post("/api/nsd/v1/subscriptions",
                                    data=subscription_req, format='json')
        self.assertEqual(201, response.status_code)

        self.user_defined_data = {
            'key1': 'value1',
            'key2': 'value2',
            'key3': 'value3',
        }
        user_defined_data_json = json.JSONEncoder().encode(self.user_defined_data)
        mock_parse_nsd.return_value = json.JSONEncoder().encode(nsd_data)
        VnfPackageModel(
            vnfPackageId="111",
            vnfdId="vcpe_vfw_zte_1_0"
        ).save()

        PnfPackageModel(
            pnfPackageId="112",
            pnfdId="m6000_s"
        ).save()

        NSPackageModel(
            nsPackageId='d0ea5ec3-0b98-438a-9bea-488230cff174',
            operationalState='DISABLED',
            usageState='NOT_IN_USE',
            userDefinedData=user_defined_data_json,
        ).save()

        with open('nsd_content.txt', 'wt') as fp:
            fp.write('test')
        with open('nsd_content.txt', 'rt') as fp:
            resp = self.client.put(
                "/api/nsd/v1/ns_descriptors/d0ea5ec3-0b98-438a-9bea-488230cff174/nsd_content",
                {'file': fp},
            )
        file_content = ''
        with open(os.path.join(CATALOG_ROOT_PATH, 'd0ea5ec3-0b98-438a-9bea-488230cff174/nsd_content.txt')) as fp:
            data = fp.read()
            file_content = '%s%s' % (file_content, data)
        ns_pkg = NSPackageModel.objects.filter(nsPackageId="d0ea5ec3-0b98-438a-9bea-488230cff174")
        self.assertEqual("b632bddc-bccd-4180-bd8d-4e8a9578eff7", ns_pkg[0].nsdId)
        self.assertEqual(const.PKG_STATUS.ONBOARDED, ns_pkg[0].onboardingState)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(None, resp.data)
        self.assertEqual(file_content, 'test')
        os.remove('nsd_content.txt')
        expect_callbackuri = "http://callbackuri.com"
        expect_notification = {
            'id': "1111",
            'notificationType': const.NSD_NOTIFICATION_TYPE.NSD_ONBOARDING,
            'timeStamp': "nowtime()",
            'nsdInfoId': "d0ea5ec3-0b98-438a-9bea-488230cff174",
            'nsdId': "b632bddc-bccd-4180-bd8d-4e8a9578eff7",
            "subscriptionId": "1111",
            '_links': {
                'subscription': {
                    'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                                   pub_config.MSB_SERVICE_PORT,
                                                   const.NSDM_SUBSCRIPTION_ROOT_URI,
                                                   "1111")},
                'nsdInfo': {
                    'href': 'http://%s:%s/%s/ns_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                   pub_config.MSB_SERVICE_PORT,
                                                                   const.NSD_URL_PREFIX,
                                                                   "d0ea5ec3-0b98-438a-9bea-488230cff174")
                }
            }
        }
        mock_requests_post.assert_called_with(expect_callbackuri, data=expect_notification,
                                              auth=HTTPBasicAuth("username", "password"),
                                              headers={'Connection': 'close'})


class NotificationTest(TestCase):
    def setUp(self):
        NsdmSubscriptionModel(subscriptionid="1",
                              callback_uri="http://127.0.0.1/self",
                              notificationTypes=const.NOTIFICATION_TYPES,
                              nsdId="nsdid1",
                              nsdInfoId="nsdinfoid1",
                              pnfdInfoIds="pnfdInfoIds1",
                              pnfdId="pnfdId1"
                              ).save()

    def tearDown(self):
        NsdmSubscriptionModel.objects.all().delete()

    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_nsdpkg_notify(self, mock_nowtime, mock_uuid, mock_requests_post):
        mock_nowtime.return_value = "nowtime()"
        mock_uuid.return_value = "1111"
        notify = NsdNotifications(const.NSD_NOTIFICATION_TYPE.NSD_ONBOARDING_FAILURE,
                                  nsd_info_id="nsdinfoid1",
                                  nsd_id="nsdid1",
                                  failure_details="NSD(nsdid1) already exists.", operational_state=None)
        notify.send_notification()
        expect_callbackuri = "http://127.0.0.1/self"
        expect_notification = {
            'id': "1111",
            'notificationType': const.NSD_NOTIFICATION_TYPE.NSD_ONBOARDING_FAILURE,
            'timeStamp': "nowtime()",
            'nsdInfoId': "nsdinfoid1",
            'nsdId': "nsdid1",
            'onboardingFailureDetails': "NSD(nsdid1) already exists.",
            "subscriptionId": "1",
            '_links': {
                'subscription': {
                    'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                                   pub_config.MSB_SERVICE_PORT,
                                                   const.NSDM_SUBSCRIPTION_ROOT_URI,
                                                   "1")},
                'nsdInfo': {
                    'href': 'http://%s:%s/%s/ns_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                   pub_config.MSB_SERVICE_PORT,
                                                                   const.NSD_URL_PREFIX,
                                                                   "nsdinfoid1")
                }
            }
        }
        mock_requests_post.assert_called_with(expect_callbackuri, data=expect_notification, headers={'Connection': 'close'})

    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_pnfpkg_notify(self, mock_nowtime, mock_uuid, mock_requests_post):
        mock_nowtime.return_value = "nowtime()"
        mock_uuid.return_value = "1111"
        notify = PnfNotifications(const.NSD_NOTIFICATION_TYPE.PNFD_ONBOARDING,
                                  pnfd_info_id="pnfdInfoIds1",
                                  pnfd_id='pnfdId1',
                                  failure_details=None)
        notify.send_notification()
        expect_callbackuri = "http://127.0.0.1/self"
        expect_notification = {
            'id': "1111",
            'notificationType': const.NSD_NOTIFICATION_TYPE.PNFD_ONBOARDING,
            'timeStamp': "nowtime()",
            'pnfdInfoIds': "pnfdInfoIds1",
            'pnfdId': "pnfdId1",
            "subscriptionId": "1",
            '_links': {
                'subscription': {
                    'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                                   pub_config.MSB_SERVICE_PORT,
                                                   const.NSDM_SUBSCRIPTION_ROOT_URI,
                                                   "1")},
                'pnfdInfo': {
                    'href': 'http://%s:%s/%s/pnf_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                    pub_config.MSB_SERVICE_PORT,
                                                                    const.NSD_URL_PREFIX,
                                                                    "pnfdInfoIds1")
                }
            }
        }
        mock_requests_post.assert_called_with(expect_callbackuri, data=expect_notification,
                                              headers={'Connection': 'close'})
