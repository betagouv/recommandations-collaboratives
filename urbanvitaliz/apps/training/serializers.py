from rest_framework import serializers

from .models import ChallengeDefinition, Challenge


class ChallengeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeDefinition
        fields = [
            "code",
            "name",
            "description",
            "icon_name",
            "next_challenge",
        ]


class ChallengeSerializer(serializers.ModelSerializer):
    definition = ChallengeDefinitionSerializer(
        source="challenge_definition", read_only=True, many=False
    )

    class Meta:
        model = Challenge
        fields = [
            "definition",
            "acquired",
            "acquired_on",
        ]
