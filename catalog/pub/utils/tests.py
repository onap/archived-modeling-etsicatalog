# Copyright 2018 ZTE Corporation.
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

import platform
import unittest
import mock

from . import fileutil
import urllib
from . import syscomm
from . import timeutil
from . import values

from catalog.pub.database.models import JobStatusModel, JobModel, VnfPkgSubscriptionModel, \
    VnfPackageModel, NsdmSubscriptionModel
from catalog.pub.utils.jobutil import JobUtil
from catalog.pub.utils.notificationsutil import NotificationsUtil, prepare_nsd_notification, \
    prepare_pnfd_notification, prepare_vnfpkg_notification
from catalog.packages import const
from catalog.pub.config import config as pub_config
import catalog.pub.utils.timeutil


class MockReq():
    def read(self):
        return "1"

    def close(self):
        pass


class UtilsTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_and_delete_dir(self):
        dirs = "abc/def/hij"
        fileutil.make_dirs(dirs)
        fileutil.make_dirs(dirs)
        fileutil.delete_dirs(dirs)

    @mock.patch.object(urllib.request, 'urlopen')
    def test_download_file_from_http(self, mock_urlopen):
        mock_urlopen.return_value = MockReq()
        fileutil.delete_dirs("abc")
        is_ok, f_name = fileutil.download_file_from_http("1", "abc", "1.txt")
        self.assertTrue(is_ok)
        if 'Windows' in platform.system():
            self.assertTrue(f_name.endswith("abc\\1.txt"))
        else:
            self.assertTrue(f_name.endswith("abc/1.txt"))
        fileutil.delete_dirs("abc")

    def test_query_job_status(self):
        job_id = "1"
        JobStatusModel.objects.filter().delete()
        JobStatusModel(
            indexid=1,
            jobid=job_id,
            status="success",
            progress=10
        ).save()
        JobStatusModel(
            indexid=2,
            jobid=job_id,
            status="success",
            progress=50
        ).save()
        JobStatusModel(
            indexid=3,
            jobid=job_id,
            status="success",
            progress=100
        ).save()
        jobs = JobUtil.query_job_status(job_id)
        self.assertEqual(1, len(jobs))
        self.assertEqual(3, jobs[0].indexid)
        jobs = JobUtil.query_job_status(job_id, 1)
        self.assertEqual(2, len(jobs))
        self.assertEqual(3, jobs[0].indexid)
        self.assertEqual(2, jobs[1].indexid)
        JobStatusModel.objects.filter().delete()

    def test_is_job_exists(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        self.assertTrue(JobUtil.is_job_exists(job_id))
        JobModel.objects.filter().delete()

    def test_create_job(self):
        job_id = "5"
        JobModel.objects.filter().delete()
        JobUtil.create_job(
            inst_type="1",
            jobaction="2",
            inst_id="3",
            user="4",
            job_id=5,
            res_name="6")
        self.assertEqual(1, len(JobModel.objects.filter(jobid=job_id)))
        JobModel.objects.filter().delete()

    def test_clear_job(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobUtil.clear_job(job_id)
        self.assertEqual(0, len(JobModel.objects.filter(jobid=job_id)))

    def test_add_job_status_when_job_is_not_created(self):
        JobModel.objects.filter().delete()
        self.assertRaises(
            Exception,
            JobUtil.add_job_status,
            job_id="1",
            progress=1,
            status_decs="2",
            error_code="0"
        )

    def test_add_job_status_normal(self):
        job_id = "1"
        JobModel.objects.filter().delete()
        JobStatusModel.objects.filter().delete()
        JobModel(
            jobid=job_id,
            jobtype="1",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobUtil.add_job_status(
            job_id="1",
            progress=1,
            status_decs="2",
            error_code="0"
        )
        self.assertEqual(1, len(JobStatusModel.objects.filter(jobid=job_id)))
        JobStatusModel.objects.filter().delete()
        JobModel.objects.filter().delete()

    def test_clear_job_status(self):
        job_id = "1"
        JobStatusModel.objects.filter().delete()
        JobStatusModel(
            indexid=1,
            jobid=job_id,
            status="success",
            progress=10
        ).save()
        JobUtil.clear_job_status(job_id)
        self.assertEqual(0, len(JobStatusModel.objects.filter(jobid=job_id)))

    def test_get_unfinished_jobs(self):
        JobModel.objects.filter().delete()
        JobModel(
            jobid="11",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobModel(
            jobid="22",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        JobModel(
            jobid="33",
            jobtype="InstVnf",
            jobaction="2",
            resid="3",
            status=0
        ).save()
        progresses = JobUtil.get_unfinished_jobs(
            url_prefix="/vnfinst",
            inst_id="3",
            inst_type="InstVnf"
        )
        expect_progresses = ['/vnfinst/11', '/vnfinst/22', '/vnfinst/33']
        self.assertEqual(expect_progresses, progresses)
        JobModel.objects.filter().delete()

    def test_fun_name(self):
        self.assertEqual("test_fun_name", syscomm.fun_name())

    def test_now_time(self):
        self.assertIn(":", timeutil.now_time())
        self.assertIn("-", timeutil.now_time())

    def test_ignore_case_get(self):
        data = {
            "Abc": "def",
            "HIG": "klm"
        }
        self.assertEqual("def", values.ignore_case_get(data, 'ABC'))
        self.assertEqual("def", values.ignore_case_get(data, 'abc'))
        self.assertEqual("klm", values.ignore_case_get(data, 'hig'))
        self.assertEqual("bbb", values.ignore_case_get(data, 'aaa', 'bbb'))


class NotificationTest(unittest.TestCase):
    def setUp(self):
        VnfPackageModel(vnfPackageId="vnfpkgid1",
                        vnfdId="vnfdid1"
                        ).save()

        VnfPkgSubscriptionModel(subscription_id="1",
                                callback_uri="http://127.0.0.1/self",
                                notification_types=const.NOTIFICATION_TYPES,
                                vnfd_id="vnfdid1",
                                vnf_pkg_id="vnfpkgid1"
                                ).save()

        NsdmSubscriptionModel(subscriptionid="1",
                              callback_uri="http://127.0.0.1/self",
                              notificationTypes=const.NOTIFICATION_TYPES,
                              nsdId="nsdid1",
                              nsdInfoId="nsdinfoid1",
                              pnfdInfoIds="pnfdInfoIds1",
                              pnfdId="pnfdId1"
                              ).save()

    def tearDown(self):
        VnfPackageModel.objects.all().delete()
        VnfPkgSubscriptionModel.objects.all().delete()

    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_vnfpkg_notify(self, mock_nowtime, mock_uuid, mock_requests_post):
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

    @mock.patch("requests.post")
    @mock.patch("uuid.uuid4")
    @mock.patch.object(catalog.pub.utils.timeutil, "now_time")
    def test_nsdpkg_notify(self, mock_nowtime, mock_uuid, mock_requests_post):
        mock_nowtime.return_value = "nowtime()"
        mock_uuid.return_value = "1111"
        notification_content = prepare_nsd_notification("nsdinfoid1", "nsdid1",
                                                        const.NSD_NOTIFICATION_TYPE.NSD_ONBOARDING_FAILURE,
                                                        "NSD(nsdid1) already exists.", operational_state=None)
        filters = {
            'nsdInfoId': 'nsdInfoId',
            'nsdId': 'nsdId',
        }
        NotificationsUtil().send_notification(notification_content, filters, False)
        expect_callbackuri = "http://127.0.0.1/self"
        expect_notification = {
            'id': "1111",
            'notificationType': const.NSD_NOTIFICATION_TYPE.NSD_ONBOARDING_FAILURE,
            'timeStamp': "nowtime()",
            'nsdInfoId': "nsdinfoid1",
            'nsdId': "nsdid1",
            'onboardingFailureDetails': "NSD(nsdid1) already exists.",
            'nsdOperationalState': None,
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
        notification_content = prepare_pnfd_notification("pnfdInfoIds1", 'pnfdId1',
                                                         const.NSD_NOTIFICATION_TYPE.PNFD_ONBOARDING)
        filters = {
            'pnfdId': 'pnfdId',
            'pnfdInfoIds': 'pnfdInfoIds',
        }
        NotificationsUtil().send_notification(notification_content, filters, False)
        expect_callbackuri = "http://127.0.0.1/self"
        expect_notification = {
            'id': "1111",
            'notificationType': const.NSD_NOTIFICATION_TYPE.PNFD_ONBOARDING,
            'timeStamp': "nowtime()",
            'pnfdInfoIds': "pnfdInfoIds1",
            'pnfdId': "pnfdId1",
            'onboardingFailureDetails': None,
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
