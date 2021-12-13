from rest_framework import serializers

from .models import Commune


class CommuneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Commune

        fields = ["name", "insee", "postal"]
