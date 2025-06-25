from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class LLMPrompt(models.Model):
    name = models.CharField(max_length=64)
    text = models.TextField()


class LLMConfig(models.Model):
    model_name = models.CharField(max_length=64)  #     llama-3.2-1b-instruct


class Summary(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    text = models.TextField()
    config = models.ForeignKey(
        LLMConfig, null=True, blank=True, on_delete=models.SET_NULL
    )
    prompt = models.ForeignKey(
        LLMPrompt, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
