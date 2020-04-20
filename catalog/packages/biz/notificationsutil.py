# Copyright 2019 ZTE Corporation.
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
import logging
import traceback
import uuid

import requests
from django.db.models import Q
from requests.auth import HTTPBasicAuth
from rest_framework import status

import catalog.pub.utils.timeutil
from catalog.packages import const
from catalog.packages.serializers.vnf_pkg_notifications import PkgChangeNotificationSerializer, \
    PkgOnboardingNotificationSerializer
from catalog.pub.config import config as pub_config
from catalog.pub.database.models import VnfPackageModel, VnfPkgSubscriptionModel, NsdmSubscriptionModel
from catalog.pub.utils.values import remove_none_key

logger = logging.getLogger(__name__)


class NotificationsUtil(object):
    def __init__(self, notification_type):
        self.notification_type = notification_type
        self.notifyserializer = None

    def prepare_notification(self, **kwargs):
        pass

    def send_notification(self):
        notification = self.prepare_notification()

        subscriptions_filter = {v + "__contains": notification[k] for k, v in self.filter.items()}
        subscriptions_filter = remove_none_key(subscriptions_filter)
        logger.debug('send_notification subscriptions_filter = %s' % subscriptions_filter)
        q1 = Q()
        q1.connector = 'OR'
        for k, v in subscriptions_filter.items():
            q1.children.append((k, v))

        subscriptions = self.SubscriptionModel.objects.filter(q1)
        if not subscriptions.exists():
            logger.info("No subscriptions created for the filter %s" % notification)
            return
        logger.info("Start sending notifications")
        for sub in subscriptions:
            # set subscription id
            notification["subscriptionId"] = sub.get_subscription_id()
            notification['_links']['subscription'] = {
                'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                               pub_config.MSB_SERVICE_PORT,
                                               self.subscription_root_uri,
                                               notification["subscriptionId"])
            }
            callbackuri = sub.callback_uri
            """
            auth_info = json.loads(sub.auth_info)
            if auth_info["authType"] == const.OAUTH2_CLIENT_CREDENTIALS:
                pass
            """
            if self.notifyserializer:
                serialized_data = self.notifyserializer(data=notification)
                if not serialized_data.is_valid():
                    logger.error('Notification Data is invalid:%s.' % serialized_data.errors)

            if sub.auth_info:
                self.post_notification(callbackuri, notification, auth_info=json.loads(sub.auth_info))
            else:
                self.post_notification(callbackuri, notification)

    def post_notification(self, callbackuri, notification, auth_info=None):
        try:
            if auth_info:
                if const.BASIC in auth_info.get("authType", ''):
                    params = auth_info.get("paramsBasic", {})
                    username = params.get("userName")
                    password = params.get("password")
                    resp = requests.post(callbackuri,
                                         data=json.dumps(notification),
                                         headers={'Connection': 'close',
                                                  'content-type': 'application/json',
                                                  'accept': 'application/json'},
                                         auth=HTTPBasicAuth(username, password),
                                         verify=False)
                elif const.OAUTH2_CLIENT_CREDENTIALS in auth_info.get("authType", ''):
                    # todo
                    pass
                else:
                    # todo
                    pass
            else:
                resp = requests.post(callbackuri,
                                     data=json.dumps(notification),
                                     headers={'Connection': 'close',
                                              'content-type': 'application/json',
                                              'accept': 'application/json'},
                                     verify=False)

            if resp.status_code == status.HTTP_204_NO_CONTENT:
                logger.info("Sending notification to %s successfully.", callbackuri)
            else:
                logger.error("Sending notification to %s failed: %s" % (callbackuri, resp))
        except:
            logger.error("Post notification failed.")
            logger.error(traceback.format_exc())


class PkgNotifications(NotificationsUtil):
    def __init__(self, notification_type, vnf_pkg_id, change_type=None, operational_state=None):
        super(PkgNotifications, self).__init__(notification_type)
        self.filter = {
            'vnfdId': 'vnfd_id',
            'vnfPkgId': 'vnf_pkg_id'
        }
        self.vnf_pkg_id = vnf_pkg_id
        self.change_type = change_type
        self.operational_state = operational_state
        self.SubscriptionModel = VnfPkgSubscriptionModel
        self.subscription_root_uri = const.VNFPKG_SUBSCRIPTION_ROOT_URI
        if self.notification_type == "VnfPackageChangeNotification":
            self.notifyserializer = PkgChangeNotificationSerializer
        else:
            self.notifyserializer = PkgOnboardingNotificationSerializer

    def prepare_notification(self):
        logger.info('Start to prepare Pkgnotification')

        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=self.vnf_pkg_id)
        vnfd_id = None
        if vnf_pkg:
            vnfd_id = vnf_pkg[0].vnfdId
        notification_content = {
            'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
            'notificationType': self.notification_type,
            # set 'subscriptionId' after filtering for subscribers
            'timeStamp': catalog.pub.utils.timeutil.now_time(),
            'vnfPkgId': self.vnf_pkg_id,
            'vnfdId': vnfd_id,
            '_links': {
                'vnfPackage': {
                    'href': 'http://%s:%s/%s/vnf_packages/%s' % (pub_config.MSB_SERVICE_IP,
                                                                 pub_config.MSB_SERVICE_PORT,
                                                                 const.PKG_URL_PREFIX,
                                                                 self.vnf_pkg_id)
                }
            }
        }

        if self.notification_type == "VnfPackageChangeNotification":
            notification_content['changeType'] = self.change_type
            notification_content['operationalState'] = self.operational_state

        return notification_content


class NsdNotifications(NotificationsUtil):
    def __init__(self, notification_type, nsd_info_id, nsd_id, failure_details=None, operational_state=None):
        super(NsdNotifications, self).__init__(notification_type)
        self.filter = {
            'nsdInfoId': 'nsdInfoId',
            'nsdId': 'nsdId',
        }
        self.SubscriptionModel = NsdmSubscriptionModel
        self.subscription_root_uri = const.NSDM_SUBSCRIPTION_ROOT_URI
        self.nsd_info_id = nsd_info_id
        self.nsd_id = nsd_id
        self.failure_details = failure_details
        self.operational_state = operational_state
        # todo:
        # if self.notification_type == "VnfPackageChangeNotification":
        #     self.notifyserializer = PkgChangeNotificationSerializer
        # else:
        #     self.notifyserializer = PkgOnboardingNotificationSerializer

    def prepare_notification(self):
        logger.info('Start to prepare Nsdnotification')

        notification_content = {
            'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
            'notificationType': self.notification_type,
            # set 'subscriptionId' after filtering for subscribers
            'timeStamp': catalog.pub.utils.timeutil.now_time(),
            'nsdInfoId': self.nsd_info_id,
            'nsdId': self.nsd_id,
            '_links': {
                'nsdInfo': {
                    'href': 'http://%s:%s/%s/ns_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                   pub_config.MSB_SERVICE_PORT,
                                                                   const.NSD_URL_PREFIX,
                                                                   self.nsd_info_id)
                }
            }
        }
        if self.notification_type == "NsdOnboardingFailureNotification":
            notification_content['onboardingFailureDetails'] = self.failure_details
        if self.notification_type == "NsdChangeNotification":
            notification_content['nsdOperationalState'] = self.operational_state
        return notification_content


class PnfNotifications(NotificationsUtil):
    def __init__(self, notification_type, pnfd_info_id, pnfd_id, failure_details=None):
        super(PnfNotifications, self).__init__(notification_type)
        self.filter = {
            'pnfdId': 'pnfdId',
            'pnfdInfoIds': 'pnfdInfoIds',
        }
        self.SubscriptionModel = NsdmSubscriptionModel
        self.subscription_root_uri = const.NSDM_SUBSCRIPTION_ROOT_URI
        self.pnfd_info_id = pnfd_info_id
        self.pnfd_id = pnfd_id
        self.failure_details = failure_details
        # todo
        # if self.notification_type == "VnfPackageChangeNotification":
        #     self.notifyserializer = PkgChangeNotificationSerializer
        # else:
        #     self.notifyserializer = PkgOnboardingNotificationSerializer

    def prepare_notification(self, *args, **kwargs):
        logger.info('Start to prepare Pnfnotification')
        notification_content = {
            'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
            'notificationType': self.notification_type,
            # set 'subscriptionId' after filtering for subscribers
            'timeStamp': catalog.pub.utils.timeutil.now_time(),
            'pnfdInfoIds': self.pnfd_info_id,
            'pnfdId': self.pnfd_id,
            '_links': {
                'pnfdInfo': {
                    'href': 'http://%s:%s/%s/pnf_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                    pub_config.MSB_SERVICE_PORT,
                                                                    const.NSD_URL_PREFIX,
                                                                    self.pnfd_info_id)
                }
            }
        }
        if self.notification_type == "PnfdOnboardingFailureNotification":
            notification_content['onboardingFailureDetails'] = self.failure_details
        return notification_content
