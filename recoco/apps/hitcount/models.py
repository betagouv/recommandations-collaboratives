from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from .managers import HitCountManager, HitCountOnSiteManager


class HitCount(TimeStampedModel):
    """
    Inspired from the [django-hitcount](https://django-hitcount.readthedocs.io/en/latest/) 3rdparty lib, but adapted to our needs.
    """

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    content_object_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="hitcount_set_for_content",
    )
    content_object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_object_ct", "content_object_id")

    context_object_ct = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="hitcount_set_for_context",
        null=True,
        blank=True,
    )
    context_object_id = models.PositiveIntegerField(null=True, blank=True)
    context_object = GenericForeignKey("context_object_ct", "context_object_id")

    objects = HitCountManager()
    on_site = HitCountOnSiteManager()

    class Meta:
        verbose_name = _("hit count")
        verbose_name_plural = _("hit counts")
        ordering = ("-created",)
        get_latest_by = "modified"
        unique_together = (
            "site",
            "content_object_ct",
            "content_object_id",
            "context_object_ct",
            "context_object_id",
        )

    def __str__(self):
        hit_count_str = f"{self.content_object_ct.name}-{self.content_object_id}"
        if self.context_object and self.context_object_id:
            hit_count_str += (
                f" ({self.context_object_ct.name}-{self.context_object_id})"
            )
        return hit_count_str


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
