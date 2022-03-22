from rest_framework import serializers

from .models import Commune, Department


class DepartmentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Department

        fields = ["name", "code"]


class CommuneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Commune

        fields = ["name", "insee", "postal", "department"]

    department = DepartmentSerializer(read_only=True)
