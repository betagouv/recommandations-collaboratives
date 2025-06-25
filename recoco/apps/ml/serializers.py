# encoding: utf-8

"""
authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2025-06-25 17:44:55 CET
"""

from rest_framework import serializers

from .models import LLMConfig, LLMPrompt, Summary


class LLMConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LLMConfig
        fields = ["model_name"]


class LLMPromptSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LLMPrompt
        fields = ["text"]


class SummarySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Summary
        fields = ["id", "original_content", "text", "prompt", "config"]

    prompt = LLMPromptSerializer(read_only=True, many=False)
    config = LLMConfigSerializer(read_only=True, many=False)
    original_content = serializers.SerializerMethodField()

    def get_original_content(self, obj):
        return obj.content_object.to_markdown()
