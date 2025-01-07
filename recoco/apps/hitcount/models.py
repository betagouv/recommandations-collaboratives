from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel


class HitCount(TimeStampedModel):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    content_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="hitcount_set_for_content",
    )
    content_object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_ct", "content_object_id")

    context_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="hitcount_set_for_context",
        null=True,
        blank=True,
    )
    context_object_id = models.PositiveIntegerField(null=True, blank=True)
    context_object = GenericForeignKey("context_ct", "context_object_id")

    class Meta:
        verbose_name = _("hit count")
        verbose_name_plural = _("hit counts")
        ordering = ("-created",)
        get_latest_by = "modified"
        unique_together = (
            "site",
            "content_ct",
            "content_object_id",
            "context_ct",
            "context_object_id",
        )


class Hit(TimeStampedModel):
    user_agent = models.CharField(max_length=255, editable=False)
    user = models.ForeignKey(User, editable=False, on_delete=models.CASCADE)
    hitcount = models.ForeignKey(
        HitCount, editable=False, on_delete=models.CASCADE, related_name="hits"
    )

    class Meta:
        verbose_name = _("hit")
        verbose_name_plural = _("hits")
        ordering = ("-created",)
        get_latest_by = "created"
