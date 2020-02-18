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
import os
import shutil
import logging
import tempfile
import traceback
import urllib
import zipfile

logger = logging.getLogger(__name__)


def make_dirs(path):
    if not os.path.exists(path):
        os.makedirs(path, 0o777)


def delete_dirs(path):
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
    except Exception as e:
        logger.error(traceback.format_exc())
        logger.error("Failed to delete %s:%s", path, e.args[0])


def download_file_from_http(url, local_dir, file_name):
    local_file_name = os.path.join(local_dir, file_name)
    is_download_ok = False
    try:
        make_dirs(local_dir)
        req = urllib.request.urlopen(url)
        save_file = open(local_file_name, 'w')
        save_file.write(req.read())
        save_file.close()
        req.close()
        is_download_ok = True
    except:
        logger.error(traceback.format_exc())
        logger.error("Failed to download %s to %s.", url, local_file_name)
    return is_download_ok, local_file_name


def unzip_file(zip_src, dst_dir, csar_path):
    logger.debug("unzip_file %s to %s.", zip_src, dst_dir)
    if os.path.exists(zip_src):
        logger.debug("unzip_file %s.", zip_src)
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
        return os.path.join(dst_dir, csar_path)
    else:
        return ""


def unzip_csar(zip_src, dst_dir):
    if os.path.exists(zip_src):
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
        return dst_dir
    else:
        logger.error("%s doesn't exist", zip_src)
        return ""


def unzip_csar_to_tmp(zip_src):
    dirpath = tempfile.mkdtemp()
    zip_ref = zipfile.ZipFile(zip_src, 'r')
    zip_ref.extractall(dirpath)
    return dirpath


def get_artifact_path(vnf_path, artifact_file):
    for root, dirs, files in os.walk(vnf_path):
        if artifact_file in files:
            return os.path.join(root, artifact_file)
    return None


def end_with(_s_in, *suffix):
    array = map(_s_in.endswith, suffix)
    if True in array:
        return True
    return False


def filter_files(search_path, suffix):
    f_find = []
    file_list = os.listdir(search_path)
    for file_item in file_list:
        if end_with(file_item, suffix):
            f_find.append(file_item)
    return f_find


def recreate_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path, mode=0o777)


def copy(src_file, dest_dir, new_file_name=None):
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    if new_file_name is None:
        dst = os.path.join(dest_dir, os.path.basename(src_file))
    else:
        dst = os.path.join(dest_dir, new_file_name)
    shutil.copyfile(src_file, dst)
    shutil.copymode(src_file, dst)
