from rest_framework import serializers

from .models import DSFolder


class DSFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = DSFolder
        fields = [
            "dossier_url",
            "prefilled_count",
        ]
