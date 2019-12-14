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

import logging
import uuid
import requests
from rest_framework import status
from catalog.packages import const
from catalog.pub.database.models import VnfPkgSubscriptionModel, NsdmSubscriptionModel
from catalog.pub.database.models import VnfPackageModel
import catalog.pub.utils.timeutil
from catalog.pub.utils.values import remove_none_key
from catalog.pub.config import config as pub_config
import traceback
from django.db.models import Q


logger = logging.getLogger(__name__)


class NotificationsUtil(object):
    def __init__(self):
        pass

    def send_notification(self, notification, filters, isvnfpkg):
        subscriptions_filter = {v + "__contains": notification[k] for k, v in filters.items()}
        subscriptions_filter = remove_none_key(subscriptions_filter)
        logger.debug('send_notification subscriptions_filter = %s' % subscriptions_filter)
        q1 = Q()
        q1.connector = 'OR'
        for k, v in subscriptions_filter.items():
            q1.children.append((k, v))
        if isvnfpkg:
            subscriptions = VnfPkgSubscriptionModel.objects.filter(q1)
            subscription_root_uri = const.VNFPKG_SUBSCRIPTION_ROOT_URI
        else:
            subscriptions = NsdmSubscriptionModel.objects.filter(q1)
            subscription_root_uri = const.NSDM_SUBSCRIPTION_ROOT_URI

        if not subscriptions.exists():
            logger.info("No subscriptions created for the filters %s" % notification)
            return
        logger.info("Start sending notifications")
        for sub in subscriptions:
            # set subscription id
            if isvnfpkg:
                notification["subscriptionId"] = sub.subscription_id
            else:
                notification["subscriptionId"] = sub.subscriptionid
            notification['_links']['subscription'] = {
                'href': 'http://%s:%s/%s%s' % (pub_config.MSB_SERVICE_IP,
                                               pub_config.MSB_SERVICE_PORT,
                                               subscription_root_uri,
                                               notification["subscriptionId"])
            }
            callbackuri = sub.callback_uri
            """
            auth_info = json.loads(sub.auth_info)
            if auth_info["authType"] == const.OAUTH2_CLIENT_CREDENTIALS:
                pass
            """
            self.post_notification(callbackuri, notification)

    def post_notification(self, callbackuri, notification):
        """
        params = auth_info.get("paramsBasic", {})
        username, password = params.get("userName"), params.get("password")
        logger.info("Sending notification to %s, %s", callbackuri, params)
        resp = None
        if username:
            resp = requests.post(callbackuri,
                                 data=notification,
                                 auth=HTTPBasicAuth(username, password))
        else:
        """

        try:
            resp = requests.post(callbackuri, data=notification, headers={'Connection': 'close'})
            if resp.status_code != status.HTTP_204_NO_CONTENT:
                logger.error("Sending notification to %s failed: %s" % (callbackuri, resp.text))
            else:
                logger.info("Sending notification to %s successfully.", callbackuri)
        except:
            logger.error("Post notification failed.")
            logger.error(traceback.format_exc())


def prepare_vnfpkg_notification(vnf_pkg_id, notification_type, pkg_change_type, operational_state):
    logger.info('Start to prepare notification')
    vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
    vnfd_id = None
    if vnf_pkg:
        vnfd_id = vnf_pkg[0].vnfdId
    notification_content = {
        'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        'notificationType': notification_type,
        # set 'subscriptionId' after filtering for subscribers
        'timeStamp': catalog.pub.utils.timeutil.now_time(),
        'vnfPkgId': vnf_pkg_id,
        'vnfdId': vnfd_id,
        '_links': {
            'vnfPackage': {
                'href': 'http://%s:%s/%s/vnf_packages/%s' % (pub_config.MSB_SERVICE_IP,
                                                             pub_config.MSB_SERVICE_PORT,
                                                             const.PKG_URL_PREFIX,
                                                             vnf_pkg_id)
            }
        }
    }

    if notification_type == "VnfPackageChangeNotification":
        notification_content['changeType'] = pkg_change_type
        notification_content['operationalState'] = operational_state

    return notification_content


def prepare_nsd_notification(nsd_info_id, nsd_id, notification_type, failure_details=None, operational_state=None):
    logger.info('Start to prepare notification')
    notification_content = {
        'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        'notificationType': notification_type,
        # set 'subscriptionId' after filtering for subscribers
        'timeStamp': catalog.pub.utils.timeutil.now_time(),
        'nsdInfoId': nsd_info_id,
        'nsdId': nsd_id,
        'onboardingFailureDetails': failure_details,
        'nsdOperationalState': operational_state,
        '_links': {
            'nsdInfo': {
                'href': 'http://%s:%s/%s/ns_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                               pub_config.MSB_SERVICE_PORT,
                                                               const.NSD_URL_PREFIX,
                                                               nsd_info_id)
            }
        }
    }
    return notification_content


def prepare_pnfd_notification(pnfd_info_id, pnfd_id, notification_type, failure_details=None):
    logger.info('Start to prepare notification')
    notification_content = {
        'id': str(uuid.uuid4()),  # shall be the same if sent multiple times due to multiple subscriptions.
        'notificationType': notification_type,
        # set 'subscriptionId' after filtering for subscribers
        'timeStamp': catalog.pub.utils.timeutil.now_time(),
        'pnfdInfoIds': pnfd_info_id,
        'pnfdId': pnfd_id,
        'onboardingFailureDetails': failure_details,
        '_links': {
            'pnfdInfo': {
                'href': 'http://%s:%s/%s/pnf_descriptors/%s' % (pub_config.MSB_SERVICE_IP,
                                                                pub_config.MSB_SERVICE_PORT,
                                                                const.NSD_URL_PREFIX,
                                                                pnfd_info_id)
            }
        }
    }
    return notification_content
