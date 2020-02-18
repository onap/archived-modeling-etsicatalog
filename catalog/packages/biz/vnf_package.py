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

import json
import logging
import os

import threading
import traceback
import urllib
import uuid
import zipfile

from catalog.packages import const
from catalog.packages.biz.common import parse_file_range, read, save
from catalog.packages.biz.notificationsutil import PkgNotifications
from catalog.pub.config.config import CATALOG_ROOT_PATH, MSB_SERVICE_IP, MSB_SERVICE_PORT
from catalog.pub.database.models import VnfPackageModel, NSPackageModel
from catalog.pub.exceptions import CatalogException, ResourceNotFoundException
from catalog.pub.utils import fileutil, toscaparser
from catalog.pub.utils.values import ignore_case_get

logger = logging.getLogger(__name__)


class VnfPackage(object):

    def __init__(self):
        pass

    def create_vnf_pkg(self, data):
        user_defined_data = ignore_case_get(data, "userDefinedData", {})
        vnf_pkg_id = str(uuid.uuid4())
        VnfPackageModel.objects.create(
            vnfPackageId=vnf_pkg_id,
            onboardingState=const.PKG_STATUS.CREATED,
            operationalState=const.PKG_STATUS.DISABLED,
            usageState=const.PKG_STATUS.NOT_IN_USE,
            userDefinedData=json.dumps(user_defined_data)
        )
        data = {
            "id": vnf_pkg_id,
            "onboardingState": const.PKG_STATUS.CREATED,
            "operationalState": const.PKG_STATUS.DISABLED,
            "usageState": const.PKG_STATUS.NOT_IN_USE,
            "userDefinedData": user_defined_data,
            "_links": None
        }
        return data

    def query_multiple(self):
        pkgs_info = []
        nf_pkgs = VnfPackageModel.objects.filter()
        for nf_pkg in nf_pkgs:
            ret = fill_response_data(nf_pkg)
            pkgs_info.append(ret)
        return pkgs_info

    def query_single(self, vnf_pkg_id):
        nf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
        if not nf_pkg.exists():
            logger.error('VNF package(%s) does not exist.' % vnf_pkg_id)
            raise ResourceNotFoundException('VNF package(%s) does not exist.' % vnf_pkg_id)
        return fill_response_data(nf_pkg[0])

    def delete_vnf_pkg(self, vnf_pkg_id):
        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
        if not vnf_pkg.exists():
            logger.debug('VNF package(%s) has been deleted.' % vnf_pkg_id)
            return
        '''
        if vnf_pkg[0].operationalState != PKG_STATUS.DISABLED:
            raise CatalogException("The VNF package (%s) is not disabled" % vnf_pkg_id)
        if vnf_pkg[0].usageState != PKG_STATUS.NOT_IN_USE:
            raise CatalogException("The VNF package (%s) is in use" % vnf_pkg_id)
        '''
        del_vnfd_id = vnf_pkg[0].vnfdId
        ns_pkgs = NSPackageModel.objects.all()
        for ns_pkg in ns_pkgs:
            nsd_model = None
            if ns_pkg.nsdModel:
                nsd_model = json.JSONDecoder().decode(ns_pkg.nsdModel)
            if not nsd_model:
                continue
            for vnf in nsd_model['vnfs']:
                if del_vnfd_id == vnf["properties"]["descriptor_id"]:
                    raise CatalogException('VNFD(%s) is referenced.' % del_vnfd_id)
        vnf_pkg.delete()
        send_notification(vnf_pkg_id, const.PKG_NOTIFICATION_TYPE.CHANGE,
                          const.PKG_CHANGE_TYPE.PKG_DELETE)

        vnf_pkg_path = os.path.join(CATALOG_ROOT_PATH, vnf_pkg_id)
        fileutil.delete_dirs(vnf_pkg_path)
        logger.info('VNF package(%s) has been deleted.' % vnf_pkg_id)

    def upload(self, vnf_pkg_id, remote_file):
        logger.info('Start to upload VNF package(%s)...' % vnf_pkg_id)
        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
        # if vnf_pkg[0].onboardingState != PKG_STATUS.CREATED:
        #     logger.error("VNF package(%s) is not CREATED" % vnf_pkg_id)
        #     raise CatalogException("VNF package(%s) is not CREATED" % vnf_pkg_id)
        vnf_pkg.update(onboardingState=const.PKG_STATUS.UPLOADING)

        local_file_name = save(remote_file, vnf_pkg_id)
        logger.info('VNF package(%s) has been uploaded.' % vnf_pkg_id)
        return local_file_name

    def download(self, vnf_pkg_id, file_range):
        logger.info('Start to download VNF package(%s)...' % vnf_pkg_id)
        nf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
        if not nf_pkg.exists():
            logger.error('VNF package(%s) does not exist.' % vnf_pkg_id)
            raise ResourceNotFoundException('VNF package(%s) does not exist.' % vnf_pkg_id)
        if nf_pkg[0].onboardingState != const.PKG_STATUS.ONBOARDED:
            raise CatalogException("VNF package (%s) is not on-boarded" % vnf_pkg_id)

        local_file_path = nf_pkg[0].localFilePath
        start, end = parse_file_range(local_file_path, file_range)
        logger.info('VNF package (%s) has been downloaded.' % vnf_pkg_id)
        return read(local_file_path, start, end)

    def download_vnfd(self, vnf_pkg_id):
        logger.info('Start to download VNFD of VNF package(%s)...' % vnf_pkg_id)
        nf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
        if not nf_pkg.exists():
            logger.error('VNF package(%s) does not exist.' % vnf_pkg_id)
            raise ResourceNotFoundException('VNF package(%s) does not exist.' % vnf_pkg_id)
        if nf_pkg[0].onboardingState != const.PKG_STATUS.ONBOARDED:
            raise CatalogException("VNF package (%s) is not on-boarded" % vnf_pkg_id)

        vnfd_zip_file = self.creat_vnfd(vnf_pkg_id, nf_pkg[0].localFilePath)
        logger.info('VNFD of VNF package (%s) has been downloaded.' % vnf_pkg_id)
        return read(vnfd_zip_file, 0, os.path.getsize(vnfd_zip_file))

    def creat_vnfd(self, vnf_pkg_id, vendor_pkg_file):
        """
        Create VNFD zip file from vendor original package
        :param self:
        :param vnf_pkg_id: VNF package id (CSAR id)
        :param vendor_pkg_file: vendor original package
        :return:
        """
        vnf_package_path = os.path.join(CATALOG_ROOT_PATH, vnf_pkg_id)
        if not os.path.exists(vnf_package_path):
            os.makedirs(vnf_package_path)
        vnfd_zip_file = os.path.join(vnf_package_path, "VNFD.zip")
        if os.path.exists(vnfd_zip_file):
            return vnfd_zip_file
        else:
            if vendor_pkg_file.endswith(".csar") or vendor_pkg_file.endswith(".zip"):
                try:
                    vnfd_path = os.path.join(vnf_package_path, "vnfd")
                    with zipfile.ZipFile(vendor_pkg_file, 'r') as vendor_zip:
                        vender_files = vendor_zip.namelist()
                        for vender_file in vender_files:
                            if str(vender_file).startswith("Definitions"):
                                vendor_zip.extract(vender_file, vnfd_path)
                    with zipfile.ZipFile(vnfd_zip_file, 'w', zipfile.ZIP_DEFLATED) as vnfd_zip:
                        def_path = os.path.join(vnfd_path, "Definitions")
                        if os.path.exists(def_path):
                            def_files = os.listdir(def_path)
                            for def_file in def_files:
                                full_path = os.path.join(def_path, def_file)
                                vnfd_zip.write(full_path, def_file)
                    return vnfd_zip_file
                except Exception as e:
                    logger.error(e)
                    if os.path.exists(vnfd_zip):
                        os.remove(vnfd_zip)
                    raise e
                finally:
                    fileutil.delete_dirs(vnfd_path)


class VnfPkgUploadThread(threading.Thread):
    def __init__(self, data, vnf_pkg_id):
        threading.Thread.__init__(self)
        self.vnf_pkg_id = vnf_pkg_id
        self.data = data
        self.upload_file_name = None

    def vnf_pkg_upload_failed_handle(self, error_msg):
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=self.vnf_pkg_id)
        if vnf_pkg and vnf_pkg[0].onboardingState == const.PKG_STATUS.UPLOADING:
            vnf_pkg.update(onboardingState=const.PKG_STATUS.CREATED)

    def run(self):
        try:
            self.upload_vnf_pkg_from_uri()
            parse_vnfd_and_save(self.vnf_pkg_id, self.upload_file_name)
        except CatalogException as e:
            self.vnf_pkg_upload_failed_handle(e.args[0])
        except Exception as e:
            self.vnf_pkg_upload_failed_handle(e.args[0])

    def upload_vnf_pkg_from_uri(self):
        logger.info("Start to upload VNF packge(%s) from URI..." % self.vnf_pkg_id)
        vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=self.vnf_pkg_id)
        if vnf_pkg[0].onboardingState != const.PKG_STATUS.CREATED:
            logger.error("VNF package(%s) is not CREATED" % self.vnf_pkg_id)
            raise CatalogException("VNF package (%s) is not created" % self.vnf_pkg_id)
        vnf_pkg.update(onboardingState=const.PKG_STATUS.UPLOADING)
        send_notification(self.vnf_pkg_id, const.PKG_NOTIFICATION_TYPE.ONBOARDING,
                          const.PKG_CHANGE_TYPE.OP_STATE_CHANGE)

        uri = ignore_case_get(self.data, "addressInformation")
        response = urllib.request.urlopen(uri)

        local_file_dir = os.path.join(CATALOG_ROOT_PATH, self.vnf_pkg_id)
        self.upload_file_name = os.path.join(local_file_dir, os.path.basename(uri))
        if not os.path.exists(local_file_dir):
            fileutil.make_dirs(local_file_dir)
        with open(self.upload_file_name, "wt") as local_file:
            local_file.write(response.read())
        response.close()
        logger.info('VNF packge(%s) has been uploaded.' % self.vnf_pkg_id)


def get_mfile_data(path):
    logger.debug('get_mfile_data path %s' % path)
    files = fileutil.filter_files(path, '.mf')
    if files:
        src_file = os.path.join(path, files[0])
        src_dict_list = []
        with open(src_file, 'r') as f:
            data = f.readlines()
            for line in data:
                if line.strip() == "":
                    continue
                src_dict = {}
                k, v = line.split(':', maxsplit=1)
                if k.strip() in ["Source", "Algorithm", "Hash"]:
                    if k.strip() == "Source" and src_dict:
                        src_dict_list.extend(src_dict)
                        src_dict = {}
                    src_dict[k.strip()] = v.strip()
                    print("src_dict:%s" % src_dict)
        if src_dict:
            src_dict_list.append(src_dict)

        logger.debug('get_mfile_data: %s' % src_dict_list)
        return src_dict_list


def fill_artifacts_data(vnf_pkg_id):
    vnf_pkg_path = os.path.join(CATALOG_ROOT_PATH, vnf_pkg_id)
    if os.path.exists(vnf_pkg_path) is False:
        return None
    files = fileutil.filter_files(vnf_pkg_path, '.csar')
    for filename in files:
        logger.info('fill_artifacts_data filename (%s)...' % filename)
        dst_file_path = os.path.join(vnf_pkg_path, "tmp")
        src_file = os.path.join(vnf_pkg_path, filename)
        dst_file = os.path.join(dst_file_path, filename)
        fileutil.recreate_dir(dst_file_path)
        fileutil.copy(src_file, vnf_pkg_path, dst_file)
        artifact_vnf_file = fileutil.unzip_file(dst_file, dst_file_path, "")
        artifacts = get_mfile_data(artifact_vnf_file)
        if artifacts:
            return [{
                "artifactPath": artifact.get("Source", ""),
                "checksum": {
                    "algorithm": artifact.get("Hash", "Null"),
                    "hash": artifact.get("Algorithm", "Null")
                }
            } for artifact in artifacts]


def fill_links(pkg_id, is_onboarded=False):
    self_href = "http://%s:%s/api/vnfpkgm/v1/vnf_packages/%s" % (
        MSB_SERVICE_IP,
        MSB_SERVICE_PORT,
        pkg_id)
    links = {
        "self": {"href": self_href},
        "vnfd": {"href": "%s/%s" % (self_href, "vnfd")},
        "packageContent": {"href": "%s/%s" % (self_href, "package_content")}
    }
    if not is_onboarded:
        links.pop("vnfd")
    return links


def fill_response_data(nf_pkg):
    pkg_info = {}
    pkg_info["id"] = nf_pkg.vnfPackageId
    pkg_info["vnfdId"] = nf_pkg.vnfdId
    pkg_info["vnfProductName"] = nf_pkg.vnfdProductName
    pkg_info["vnfSoftwareVersion"] = nf_pkg.vnfSoftwareVersion
    pkg_info["vnfdVersion"] = nf_pkg.vnfdVersion
    if nf_pkg.checksum:
        pkg_info["checksum"] = json.JSONDecoder().decode(nf_pkg.checksum)
    pkg_info["softwareImages"] = None  # TODO
    pkg_info["additionalArtifacts"] = fill_artifacts_data(nf_pkg.vnfPackageId)
    pkg_info["onboardingState"] = nf_pkg.onboardingState
    pkg_info["operationalState"] = nf_pkg.operationalState
    pkg_info["usageState"] = nf_pkg.usageState
    if nf_pkg.userDefinedData:
        pkg_info["userDefinedData"] = json.JSONDecoder().decode(nf_pkg.userDefinedData)
    pkg_info["_links"] = fill_links(nf_pkg.vnfPackageId, True)
    return pkg_info


def parse_vnfd_and_save(vnf_pkg_id, vnf_pkg_path):
    logger.info('Start to process VNF package(%s)...' % vnf_pkg_id)
    vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
    vnf_pkg.update(onboardingState=const.PKG_STATUS.PROCESSING)
    vnfd_json = toscaparser.parse_vnfd(vnf_pkg_path)
    vnfd = json.JSONDecoder().decode(vnfd_json)

    if vnfd.get("vnf", "") != "":
        vnfd_id = vnfd["vnf"]["properties"].get("descriptor_id", "")
        other_pkg = VnfPackageModel.objects.filter(vnfdId=vnfd_id)
        if other_pkg and other_pkg[0].vnfPackageId != vnf_pkg_id:
            logger.error("VNF package(%s,%s) already exists.", other_pkg[0].vnfPackageId, vnfd_id)
            raise CatalogException("VNF package(%s) already exists." % vnfd_id)
        vnf_provider = vnfd["vnf"]["properties"].get("provider", "")
        vnfd_ver = vnfd["vnf"]["properties"].get("descriptor_version", "")
        vnf_software_version = vnfd["vnf"]["properties"].get("software_version", "")
        vnfd_product_name = vnfd["vnf"]["properties"].get("product_name", "")
        vnf_pkg.update(
            vnfPackageId=vnf_pkg_id,
            vnfdId=vnfd_id,
            vnfdProductName=vnfd_product_name,
            vnfVendor=vnf_provider,
            vnfdVersion=vnfd_ver,
            vnfSoftwareVersion=vnf_software_version,
            vnfdModel=vnfd_json,
            onboardingState=const.PKG_STATUS.ONBOARDED,
            operationalState=const.PKG_STATUS.ENABLED,
            usageState=const.PKG_STATUS.NOT_IN_USE,
            localFilePath=vnf_pkg_path,
            vnfPackageUri=os.path.split(vnf_pkg_path)[-1]
        )
        send_notification(vnf_pkg_id, const.PKG_NOTIFICATION_TYPE.ONBOARDING,
                          const.PKG_CHANGE_TYPE.OP_STATE_CHANGE)
    else:
        raise CatalogException("VNF propeties and metadata in VNF Package(id=%s) are empty." % vnf_pkg_id)
    logger.info('VNF package(%s) has been processed(done).' % vnf_pkg_id)


def handle_upload_failed(vnf_pkg_id):
    vnf_pkg = VnfPackageModel.objects.filter(vnfPackageId=vnf_pkg_id)
    vnf_pkg.update(onboardingState=const.PKG_STATUS.CREATED)


def send_notification(pkg_id, type, pkg_change_type, operational_state=None):
    notify = PkgNotifications(type, pkg_id, change_type=pkg_change_type,
                              operational_state=operational_state)
    notify.send_notification()
