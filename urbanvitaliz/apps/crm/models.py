from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from markdownx.utils import markdownify


class Note(models.Model):
    class Meta:
        unique_together = ("content_type", "object_id")

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )

    created_by = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="crm_notes_created"
    )

    title = models.CharField(max_length=128, verbose_name="Titre de la note")
    content = models.TextField(default="")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related = GenericForeignKey("content_type", "object_id")

    @property
    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)
