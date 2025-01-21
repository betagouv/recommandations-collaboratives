from rest_framework import serializers

from .models import Commune, Department, Region


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["name", "code"]


class CommuneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commune
        fields = ["name", "insee", "postal", "department", "latitude", "longitude"]

    department = DepartmentSerializer(read_only=True)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ["name", "code", "departments"]

    departments = DepartmentSerializer(read_only=True, many=True)
