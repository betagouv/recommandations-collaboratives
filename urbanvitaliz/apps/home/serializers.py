# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-05-16 17:44:55 CET
"""


from django.contrib.auth import models as auth_models
from rest_framework import serializers
from urbanvitaliz.apps.addressbook.serializers import OrganizationSerializer

from .models import UserProfile


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile

        fields = ["organization"]

    organization = OrganizationSerializer(read_only=True, many=False)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = auth_models.User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
        ]

    profile = UserProfileSerializer(read_only=True, many=False)
