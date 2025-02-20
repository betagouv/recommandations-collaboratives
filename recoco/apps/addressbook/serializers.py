# encoding: utf-8

"""
Models for addressbook application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-05-16 17:44:55 CET
"""

from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    FloatField,
    # HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
)

from recoco.rest_api.serializers import BaseSerializerMixin

from .models import Contact, Organization, OrganizationGroup

# OrganizationGroup serializers


class OrganizationGroupSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = OrganizationGroup
        fields = [
            "id",
            "name",
        ]


# Organization serializers


class OrganizationSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "group",
            "departments",
        ]

    def save(self, **kwargs):
        return super().save(sites=[self.current_site], **kwargs)


class OrganizationListSerializer(OrganizationSerializer):
    departments = SerializerMethodField()
    group = OrganizationGroupSerializer(read_only=True)

    # FIXME: https://sentry.incubateur.net/organizations/betagouv/issues/149134/?project=178&query=is%3Aunresolved&referrer=issue-stream&stream_index=0
    # _link = HyperlinkedIdentityField(view_name="api-addressbook-organization-detail")
    _search_rank = FloatField(source="search_rank", read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "group",
            "departments",
            # "_link",
            "_search_rank",
        ]

    def get_departments(self, obj):
        return [dep.code for dep in obj.departments.all()]


class OrganizationDetailSerializer(OrganizationListSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "group",
            "departments",
        ]


class NestedOrganizationSerializer(OrganizationListSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            # "_link",
        ]


# Contact serializers


class ContactSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = Contact
        exclude = ("site",)

    def save(self, **kwargs):
        organization = self.validated_data.get("organization")
        if (
            organization
            and self.current_site
            and not organization.sites.filter(id=self.current_site.id).exists()
        ):
            raise ValidationError(
                detail={"organization": "Organization does not belong to this site"}
            )

        return super().save(site=self.current_site, **kwargs)


class ContactListSerializer(ContactSerializer):
    organization = NestedOrganizationSerializer(read_only=True, many=False)

    # _link = HyperlinkedIdentityField(view_name="api-addressbook-contact-detail")
    _search_rank = FloatField(source="search_rank", read_only=True)

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "mobile_no",
            "division",
            "organization",
            "created",
            "modified",
            # "_link",
            "_search_rank",
        ]
        read_only_fields = fields


class ContactDetailSerializer(ContactListSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "mobile_no",
            "division",
            "organization",
            "created",
            "modified",
        ]


class NestedContactSerializer(ContactListSerializer):
    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone_no",
            "mobile_no",
            "division",
            "organization",
            # "_link",
        ]
        read_only_fields = fields
