from typing import Any

from django.apps import apps
from rest_framework import serializers

from .utils import ct_from_label


class HitInputSerializer(serializers.Serializer):
    content_object_ct = serializers.CharField()
    content_object_id = serializers.IntegerField()
    context_object_ct = serializers.CharField(required=False)
    context_object_id = serializers.IntegerField(required=False)

    def validate(self, data):
        content_object_ct = data.get("content_object_ct")
        content_object_id = data.get("content_object_id")
        context_object_ct = data.get("context_object_ct")
        context_object_id = data.get("context_object_id")

        if context_object_ct and not context_object_id:
            raise serializers.ValidationError(
                "context_object_ct is required when context_object_id is provided"
            )

        if context_object_id and not context_object_ct:
            raise serializers.ValidationError(
                "context_object_id is required when context_object_ct is provided"
            )

        content_obj_model = apps.get_model(content_object_ct)
        try:
            content_obj_model.objects.get(id=content_object_id)
        except content_obj_model.DoesNotExist as exc:
            raise serializers.ValidationError("Invalid content_object_id") from exc

        if context_object_ct:
            context_object_model = apps.get_model(context_object_ct)
            try:
                context_object_model.objects.get(id=data.get("context_object_id"))
            except context_object_model.DoesNotExist as exc:
                raise serializers.ValidationError("Invalid context_object_id") from exc

        return data

    @property
    def output_data(self) -> dict[str, Any]:
        data = {
            "content_object_ct": ct_from_label(
                self.validated_data["content_object_ct"]
            ),
            "content_object_id": self.validated_data["content_object_id"],
        }
        if self.validated_data.get("context_object_ct"):
            data.update(
                {
                    "context_object_ct": ct_from_label(
                        self.validated_data["context_object_ct"]
                    ),
                    "context_object_id": self.validated_data["context_object_id"],
                }
            )
        return data
