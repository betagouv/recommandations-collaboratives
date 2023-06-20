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
    challenge_definition = ChallengeDefinitionSerializer(read_only=True, many=False)

    class Meta:
        model = Challenge
        fields = [
            "challenge_definition",
            "acquired_on",
            "started_on",
        ]
