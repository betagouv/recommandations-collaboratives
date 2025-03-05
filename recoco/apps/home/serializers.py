# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-05-16 17:44:55 CET
"""

from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from rest_framework import serializers

from recoco.apps.addressbook.serializers import NestedOrganizationSerializer

from .models import SiteConfiguration, UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile

        fields = ["organization", "organization_position"]

    organization = NestedOrganizationSerializer(read_only=True, many=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = auth_models.User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
            "is_active",
        ]

    profile = UserProfileSerializer(read_only=True, many=False)


class SiteConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteConfiguration

        fields = [
            "legal_owner",
            "legal_address",
            "description",
            "logo_large",
            "logo_small",
        ]


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = sites_models.Site

        fields = [
            "id",
            "name",
            "domain",
            "configuration",
        ]

    configuration = SiteConfigurationSerializer(read_only=True, many=False)
