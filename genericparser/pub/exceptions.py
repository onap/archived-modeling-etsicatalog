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


class GenericparserException(Exception):
    pass


class ResourceNotFoundException(GenericparserException):
    pass


class PackageNotFoundException(GenericparserException):
    pass


class PackageHasExistsException(GenericparserException):
    pass


class VnfPkgSubscriptionException(GenericparserException):
    pass


class VnfPkgDuplicateSubscriptionException(GenericparserException):
    pass


class SubscriptionDoesNotExistsException(GenericparserException):
    pass


class NsdmBadRequestException(GenericparserException):
    pass


class NsdmDuplicateSubscriptionException(GenericparserException):
    pass


class BadRequestException(GenericparserException):
    pass


class ArtifactNotFoundException(GenericparserException):
    pass
