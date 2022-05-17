# encoding: utf-8

"""
Models for addressbook application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-05-16 17:44:55 CET
"""


from rest_framework import serializers

from .models import Organization


class OrganizationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Organization

        fields = ["name"]
