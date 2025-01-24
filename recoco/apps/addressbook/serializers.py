# encoding: utf-8

"""
Models for addressbook application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-05-16 17:44:55 CET
"""


from rest_framework.exceptions import ValidationError
from rest_framework.serializers import (
    FloatField,
    HyperlinkedModelSerializer,
    HyperlinkedRelatedField,
    ModelSerializer,
    SerializerMethodField,
)

from recoco.rest_api.serializers import BaseSerializerMixin

from .models import Contact, Organization, OrganizationGroup


class OrganizationGroupSerializer(BaseSerializerMixin, ModelSerializer):
    class Meta:
        model = OrganizationGroup
        fields = [
            "name",
        ]


class OrganizationSerializer(BaseSerializerMixin, HyperlinkedModelSerializer):
    group = HyperlinkedRelatedField(
        read_only=True, view_name="api-addressbook-organizationgroup-detail"
    )
    departments = SerializerMethodField()

    _search_rank = FloatField(source="search_rank", read_only=True)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "group",
            "departments",
            "_search_rank",
        ]

    def save(self, **kwargs):
        return super().save(sites=[self.current_site], **kwargs)

    def get_departments(self, obj):
        return [dep.code for dep in obj.departments.all()]


class NestedOrganizationSerializer(ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
        ]


class ContactCreateSerializer(BaseSerializerMixin, ModelSerializer):
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


class ContactSerializer(BaseSerializerMixin, ModelSerializer):
    # organization = HyperlinkedRelatedField(
    #     view_name="api-addressbook-organization-detail",
    #     read_only=True,
    # )
    organization = NestedOrganizationSerializer(read_only=True, many=False)

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
            "_search_rank",
        ]


class NestedContactSerializer(ModelSerializer):
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
        ]
