from rest_framework import serializers

from .models import Reminder


class ReminderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reminder
        fields = ["id", "deadline", "recipient", "origin"]
