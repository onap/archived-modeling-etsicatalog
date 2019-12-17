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

from rest_framework import serializers
from catalog.packages.const import NOTIFICATION_TYPES

PackageOperationalStateType = ["ENABLED", "DISABLED"]
PackageUsageStateType = ["IN_USE", "NOT_IN_USE"]
PackageChangeType = ["OP_STATE_CHANGE", "PKG_DELETE"]


class VersionSerializer(serializers.Serializer):
    vnfSoftwareVersion = serializers.CharField(
        help_text="VNF software version to match.",
        max_length=255,
        required=True,
        allow_null=False
    )
    vnfdVersions = serializers.ListField(
        child=serializers.CharField(),
        help_text="Match VNF packages that contain "
                  "VNF products with certain VNFD versions",
        required=False,
        allow_null=False
    )


class vnfProductsSerializer(serializers.Serializer):
    vnfProductName = serializers.CharField(
        help_text="Name of the VNF product to match.",
        max_length=255,
        required=True,
        allow_null=False
    )
    versions = VersionSerializer(
        help_text="match VNF packages that contain "
                  "VNF products with certain versions",
        required=False,
        allow_null=False
    )


class vnfProductsProvidersSerializer(serializers.Serializer):
    vnfProvider = serializers.CharField(
        help_text="Name of the VNFprovider to match.",
        max_length=255,
        required=True,
        allow_null=False
    )
    vnfProducts = vnfProductsSerializer(
        help_text="match VNF packages that contain "
                  "VNF products with certain product names, "
                  "from one particular provider",
        required=False,
        allow_null=False
    )


class PkgmNotificationsFilter(serializers.Serializer):
    notificationTypes = serializers.ListField(
        child=serializers.ChoiceField(
            required=True,
            choices=NOTIFICATION_TYPES
        ),
        help_text="Match particular notification types",
        allow_null=False,
        required=False
    )
    vnfProductsFromProviders = serializers.ListField(
        child=vnfProductsProvidersSerializer(),
        help_text="Match VNF packages that contain "
                  "VNF products from certain providers.",
        allow_null=False,
        required=False
    )
    vnfdId = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Match VNF packages with a VNFD identifier"
                  "listed in the attribute",
        required=False,
        allow_null=False
    )
    vnfPkgId = serializers.ListField(
        child=serializers.UUIDField(),
        help_text="Match VNF packages with a VNFD identifier"
                  "listed in the attribute",
        required=False,
        allow_null=False
    )
    operationalState = serializers.ListField(
        child=serializers.ChoiceField(
            required=True,
            choices=PackageOperationalStateType
        ),
        help_text="Operational state of the VNF package.",
        allow_null=False,
        required=False
    )
    usageState = serializers.ListField(
        child=serializers.ChoiceField(
            required=True,
            choices=PackageUsageStateType
        ),
        help_text="Operational state of the VNF package.",
        allow_null=False,
        required=False
    )


class LinkSerializer(serializers.Serializer):
    href = serializers.CharField(
        help_text="URI of the referenced resource.",
        required=True,
        allow_null=False,
        allow_blank=False
    )

    class Meta:
        ref_name = 'NOTIFICATION_LINKSERIALIZER'


class PkgmLinksSerializer(serializers.Serializer):
    vnfPackage = LinkSerializer(
        help_text="Link to the resource representing the VNF package to which the notified change applies.",
        required=False,
        allow_null=False
    )
    subscription = LinkSerializer(
        help_text="Link to the related subscription.",
        required=False,
        allow_null=False
    )


class PkgChangeNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification.",
        required=True,
        allow_null=False
    )
    notificationType = serializers.ChoiceField(
        help_text="Discriminator for the different notification types.",
        choices=["VnfPackageChangeNotification"],
        required=True,
        allow_null=False
    )
    timeStamp = serializers.DateTimeField(
        help_text="Date-time of the generation of the notification.",
        format="%Y-%m-%d %H:%M:%S",
        required=True,
        allow_null=False
    )
    subscriptionId = serializers.CharField(
        help_text="Identifier of the subscription that this notification relates to.",
        required=True,
        allow_null=False
    )
    vnfPkgId = serializers.UUIDField(
        help_text="Identifier of the VNF package.",
        required=True,
        allow_null=False
    )
    vnfdId = serializers.UUIDField(
        help_text="This identifier, which is managed by the VNF provider, "
                  "identifies the VNF package and the VNFD in a globally unique way.",
        required=True,
        allow_null=False
    )
    changeType = serializers.ChoiceField(
        help_text="The type of change of the VNF package.",
        choices=PackageChangeType,
        required=True,
        allow_null=False
    )
    operationalState = serializers.ChoiceField(
        help_text="New operational state of the VNF package.",
        choices=PackageOperationalStateType,
        required=False,
        allow_null=False
    )
    vnfdId = serializers.CharField(
        help_text="This identifier, which is managed by the VNF provider, "
                  "identifies the VNF package and the VNFD in a globally unique way.",
        required=True,
        allow_null=False
    )
    _links = PkgmLinksSerializer(
        help_text="Links to resources related to this resource.",
        required=True,
        allow_null=False
    )


class PkgOnboardingNotificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        help_text="Identifier of this notification.",
        required=True,
        allow_null=False
    )
    notificationType = serializers.ChoiceField(
        help_text="Discriminator for the different notification types.",
        choices=["VnfPackageOnboardingNotification"],
        required=True,
        allow_null=False
    )
    subscriptionId = serializers.CharField(
        help_text="Identifier of the subscription that this notification relates to.",
        required=True,
        allow_null=False
    )
    timeStamp = serializers.DateTimeField(
        help_text="Date-time of the generation of the notification.",
        required=True,
        allow_null=False
    )
    vnfPkgId = serializers.UUIDField(
        help_text="Identifier of the VNF package.",
        required=True,
        allow_null=False
    )
    vnfdId = serializers.UUIDField(
        help_text="This identifier, which is managed by the VNF provider, "
                  "identifies the VNF package and the VNFD in a globally unique way.",
        required=True,
        allow_null=False
    )
    _links = PkgmLinksSerializer(
        help_text="Links to resources related to this resource.",
        required=True,
        allow_null=False
    )
