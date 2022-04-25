from rest_framework import serializers

from .models import Mail


class MailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mail
        fields = ["id", "deadline", "recipient", "origin"]
