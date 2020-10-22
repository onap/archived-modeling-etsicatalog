# Copyright 2019 CMCC Technologies Co., Ltd.
import json
import logging
import time
import traceback
import uuid
from threading import Thread

from apscheduler.schedulers.background import BackgroundScheduler

from catalog.pub.database.models import VnfPackageModel
from catalog.pub.exceptions import CatalogException
from catalog.packages.biz import sdc_vnf_package, sdc_ns_package
from catalog.pub.utils.jobutil import JobUtil
from catalog.pub.utils.values import ignore_case_get

from catalog.pub.Dmaap_lib.dmaap.consumer import ConsumerClient
from catalog.pub.Dmaap_lib.dmaap.identity import IdentityClient
from catalog.pub.Dmaap_lib.dmaap.publisher import BatchPublisherClient
from catalog.pub.config.config import CONSUMER_GROUP, CONSUMER_ID, POLLING_INTERVAL, DMAAP_MR_BASE_URL
from catalog.pub.msapi import sdc

logger = logging.getLogger(__name__)

ARTIFACT_TYPES_LIST = ["TOSCA_TEMPLATE", "TOSCA_CSAR"]


class SDCController(Thread):
    def __init__(self):
        super(SDCController, self).__init__()
        self.identity = IdentityClient(DMAAP_MR_BASE_URL)
        self.scheduler = BackgroundScheduler(job_defaults={'max_instances': 3})
        self.notification_topic = ''
        self.status_topic = ''
        self.consumer = ''

        @self.scheduler.scheduled_job('interval', seconds=POLLING_INTERVAL)
        def fetch_task():
            self.fetch_notification()

    def run(self):
        try:
            description = 'nfvo catalog key for' + CONSUMER_ID
            key = self.identity.create_apikey('', description)
            topics = sdc.register_for_topics(key['apiKey'])
            self.notification_topic = topics['distrNotificationTopicName']
            self.status_topic = topics['distrStatusTopicName']
            self.consumer = ConsumerClient(DMAAP_MR_BASE_URL, self.notification_topic, CONSUMER_GROUP, CONSUMER_ID)
            self.consumer.set_api_credentials(key['apiKey'], key['apiSecret'])
            self.scheduler.start()
        except Exception as e:
            logger.error('start sdc controller failed.')
            logger.error(str(e))
            logger.error(traceback.format_exc())

    def fetch_notification(self):
        try:
            logger.info('start to fetch message from dmaap.')
            now_ms = int(time.time() * 1000)
            notification_msgs = self.consumer.fetch()
            logger.info('Receive a notification from dmaap: %s', notification_msgs)
            for notification_msg in notification_msgs:
                notification_callback = build_callback_notification(now_ms, notification_msg)
                if is_activate_callback(notification_callback):
                    process_notification(notification_callback)
        except Exception as e:
            logger.error('fetch message from dmaap failed.')
            logger.error(str(e))
            logger.error(traceback.format_exc())


def is_activate_callback(notification_callback):
    has_relevant_artifacts_in_resource = False
    has_relevant_artifacts_in_service = False
    if notification_callback['resources']:
        has_relevant_artifacts_in_resource = True
    if notification_callback['serviceArtifacts']:
        has_relevant_artifacts_in_service = True
    return has_relevant_artifacts_in_resource or has_relevant_artifacts_in_service


def build_callback_notification(now_ms, notification_msg):
    # relevant_resource_instances = build_resource_instances(notification_msg, now_ms)
    relevant_service_artifacts = handle_relevant_artifacts(notification_msg, now_ms,
                                                           notification_msg['serviceArtifacts'])
    # notification_msg['resources'] = relevant_resource_instances
    notification_msg['serviceArtifacts'] = relevant_service_artifacts
    return notification_msg


def build_resource_instances(notification_msg, now_ms):
    relevant_resource_instances = []
    resources = notification_msg['resources']
    for resource in resources:
        artifacts = resource['artifacts']
        found_relevant_artifacts = handle_relevant_artifacts(notification_msg, now_ms, artifacts)
        if found_relevant_artifacts:
            resources['artifacts'] = found_relevant_artifacts
            relevant_resource_instances.append(resources)
    return relevant_resource_instances


def handle_relevant_artifacts(notification_msg, now_ms, artifacts):
    relevant_artifacts = []
    for artifact in artifacts:
        artifact_type = artifact['artifactType']
        is_artifact_relevant = artifact_type in ARTIFACT_TYPES_LIST
        if is_artifact_relevant:
            generated_from_uuid = artifact.get('generatedFromUUID', '')
            if generated_from_uuid:
                generated_from_artifact = None
                for artifact_g in artifacts:
                    if generated_from_uuid == artifact_g['artifactUUID']:
                        generated_from_artifact = artifact_g
                        break
                if generated_from_artifact:
                    is_artifact_relevant = generated_from_artifact['artifactType'] in ARTIFACT_TYPES_LIST
                else:
                    is_artifact_relevant = False
            if is_artifact_relevant:
                artifact = set_related_artifacts(artifact, notification_msg)
                relevant_artifacts.append(artifact)

        # notification_status = send_notification_status(now_ms, notification_msg['distributionID'], artifact, is_artifact_relevant)
        # if notification_status != 'SUCCESS':
        #     logger.error("Error failed to send notification status to Dmaap.")

    return relevant_artifacts


def set_related_artifacts(artifact, notification_msg):
    related_artifacts_uuid = artifact.get('relatedArtifacts', '')
    if related_artifacts_uuid:
        related_artifacts = []
        for artifact_uuid in related_artifacts_uuid:
            related_artifacts.append(get_artifact_metadata(notification_msg, artifact_uuid))
        artifact['relatedArtifactsInfo'] = related_artifacts
    return artifact


def get_artifact_metadata(notification_msg, uuid):
    service_artifacts = notification_msg['serviceArtifacts']
    ret = None
    for artifact in service_artifacts:
        if artifact['artifactUUID'] == uuid:
            ret = artifact
            break
    resources = notification_msg['resources']
    if (not ret) and resources:
        for resource in resources:
            artifacts = resource['artifacts']
            for artifact in artifacts:
                if artifact['artifactUUID'] == uuid:
                    ret = artifact
                    break
            if ret:
                break
    return ret


def send_notification_status(status_topic, now_ms, distribution_id, artifact, is_artifact_relevant):
    logger.info('start to send notification status')
    status = 'FAIL'
    if is_artifact_relevant:
        notification_status = 'NOTIFIED'
    else:
        notification_status = 'NOT_NOTIFIED'
    request = {
        'distributionID': distribution_id,
        'consumerID': CONSUMER_ID,
        'timestamp': now_ms,
        'artifactURL': artifact['artifactURL'],
        'status': notification_status
    }
    request_json = json.JSONEncoder().encode(request)
    pub = BatchPublisherClient(DMAAP_MR_BASE_URL, status_topic, '', 'application/cambria')
    logger.info('try to send notification status: %s', request_json)

    try:
        pub.send('MyPartitionKey', request_json)
        time.sleep(1)
        stuck = pub.close(10)
        if not stuck:
            status = 'SUCCESS'
            logger.info('send notification status success.')
        else:
            logger.error('failed to send notification status, %s messages unsent', len(stuck))
    except Exception as e:
        logger.error('failed to send notification status.')
        logger.error(str(e))
        logger.error(traceback.format_exc())

    return status


def process_notification(msg):
    logger.info('Receive a callback notification, nb of resources: %s', len(msg['resources']))
    try:
        ns = sdc.get_asset(sdc.ASSETTYPE_SERVICES, msg['serviceUUID'])
        # check if the related resources exist
        resources = ns.get('resources', None)
        job_array = []
        resource_threads = []
        if resources:
            for resource in resources:
                if (resource['resoucreType'] == 'VF') and not VnfPackageModel.objects.filter(vnfPackageId=resource['resourceUUID']):
                    logger.debug("VF [%s] is not distributed.", resource['resourceUUID'])
                    # raise CatalogException("VF (%s) is not distributed." % resource['resourceUUID'])
                    logger.info("VF [%s] begin to distribute.", resource['resourceUUID'])
                    csar_id = resource['resourceUUID']
                    vim_ids = ignore_case_get(resource, "vimIds")
                    lab_vim_id = ignore_case_get(resource, "labVimId")
                    job_id = str(uuid.uuid4())
                    job_array.append(job_id)
                    resource_threads.append(sdc_vnf_package.NfDistributeThread(csar_id, vim_ids, lab_vim_id, job_id))
                    # sdc_vnf_package.NfDistributeThread(csar_id, vim_ids, lab_vim_id, job_id).start()
                else:
                    logger.debug("resource [%s] has been distributed", resource['resourceUUID'])
        for resource_thread in resource_threads:
            resource_thread.start()
        for resource_thread in resource_threads:
            resource_thread.join()
        for jobID in job_array:
            job_status = JobUtil.query_job_status(jobID)
            if job_status[0].status == 'error':
                raise CatalogException("VF resource fail to distributed.")

        service_artifacts = msg['serviceArtifacts']
        for artifact in service_artifacts:
            if artifact['artifactType'] == 'TOSCA_CSAR':
                csar_id = artifact['artifactUUID']
                sdc_ns_package.ns_on_distribute(csar_id)
    except CatalogException as e:
        logger.error("Failed to download the resource")
        logger.error(str(e))
