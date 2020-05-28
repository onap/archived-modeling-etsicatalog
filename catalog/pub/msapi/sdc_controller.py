# Copyright 2019 CMCC Technologies Co., Ltd.
import json
import logging
import os
import time
import traceback
import uuid
from threading import Thread

from apscheduler.scheduler import Scheduler

from catalog.pub.Dmaap_lib.dmaap.consumer import ConsumerClient
from catalog.pub.Dmaap_lib.dmaap.identity import IdentityClient
from catalog.pub.Dmaap_lib.dmaap.publisher import BatchPublisherClient
from catalog.pub.config.config import CONSUMER_GROUP, CONSUMER_ID, POLLING_INTERVAL, DMAAP_MR_IP, \
    DMAAP_MR_PORT
from catalog.pub.msapi import sdc

logger = logging.getLogger(__name__)

DMAAP_MR_BASE_URL = "https://%s:%s" % (DMAAP_MR_IP, DMAAP_MR_PORT)
ARTIFACT_TYPES_LIST = ["TOSCA_TEMPLATE", "TOSCA_CSAR"]


class SDCController(Thread):
    def __init__(self):
        super(SDCController, self).__init__()
        self.identity = IdentityClient(DMAAP_MR_BASE_URL)
        self.scheduler = Scheduler(standalone=True)
        self.notification_topic = ''
        self.status_topic = ''
        self.consumer = ''

        @self.scheduler.interval_schedule(seconds=POLLING_INTERVAL)
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
            logger.error(e.message)
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
            logger.error(e.message)
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
        logger.error(e.message)
        logger.error(traceback.format_exc())

    return status


def process_notification(msg):
    logger.info('Receive a callback notification, nb of resources: %s', len(msg['resources']))
    service_artifacts = msg['serviceArtifacts']
    for artifact in service_artifacts:
        if artifact['artifactType'] == 'TOSCA_CSAR':
            csar_id = artifact['artifactUUID']
            download_url = artifact['artifactURL']
            localhost_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ns_csar_base = os.path.join(localhost_dir, "csars", "ns")
            local_path = os.path.join(ns_csar_base, msg['distributionID'])
            file_name = artifact['artifactName']
            csar_version = artifact['artifactVersion']
            sdc.download_artifacts(download_url, local_path, file_name)
            # call ns package upload
            data = {
                'nsPackageId': csar_id,
                'nsPackageVersion': csar_version,
                'csarName': file_name,
                'csarDir': local_path
            }
            jobid = uuid.uuid4()
            # NsPackageParser(data, jobid).start()
            logger.debug(data, jobid)
