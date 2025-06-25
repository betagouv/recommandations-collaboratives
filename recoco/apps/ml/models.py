from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from model_utils.models import TimeStampedModel


class LLMPrompt(models.Model):
    name = models.CharField(max_length=64)
    text = models.TextField()

    def __str__(self):
        return self.name


class LLMConfig(models.Model):
    model_name = models.CharField(max_length=64)  #     llama-3.2-1b-instruct

    def __str__(self):
        return self.model_name


class Summary(TimeStampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    text = models.TextField(null=True, blank=True)
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


class Comparison(TimeStampedModel):
    CHOICES = ((0, "None Meaningful"), (1, "Summary 1"), (2, "Summary 2"))

    summary1 = models.ForeignKey(
        Summary, on_delete=models.CASCADE, related_name="comparison_1"
    )
    summary2 = models.ForeignKey(
        Summary, on_delete=models.CASCADE, related_name="comparison_2"
    )

    choice = models.IntegerField(choices=CHOICES, null=True)

    user = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="ml_comparisons"
    )

    class Meta:
        unique_together = [["summary1", "summary2", "user"]]
