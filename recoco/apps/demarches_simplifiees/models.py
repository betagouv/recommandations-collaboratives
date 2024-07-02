from django.contrib.auth.models import User
from django.db import models, transaction
from model_utils.models import TimeStampedModel

from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.tasks.models import Task

from .utils import hash_data


class DSResource(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    schema = models.JSONField(default=dict, null=True, blank=True)
    resource = models.ForeignKey(
        Resource, null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Démarche simplifiée"
        verbose_name_plural = "Démarches simplifiées"
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def number(self) -> int:
        return self.schema.get("number")


class DSFolder(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    ds_resource = models.ForeignKey(
        DSResource,
        on_delete=models.CASCADE,
    )

    action = models.ForeignKey(
        Task,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    dossier_id = models.CharField(max_length=255)
    dossier_url = models.URLField()
    dossier_number = models.IntegerField()
    dossier_prefill_token = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    content = models.JSONField()
    content_hash = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Dossier pré-rempli"
        verbose_name_plural = "Dossiers pré-remplis"
        ordering = ["-created"]
        indexes = [
            models.Index(fields=["project", "ds_resource", "content_hash"]),
        ]

    def __str__(self) -> str:
        return self.dossier_id

    def save(self, *args, **kwargs):
        self.content_hash = hash_data(dict(self.content))
        super().save(*args, **kwargs)

    def update_or_create_action(self):
        # FIXME: figure out how is the author of this action
        author = User.objects.filter(is_staff=True).first()

        content = f"[Lien vers la démarche simplifiée pré-remplie]({self.dossier_url})"

        action_data = {
            "site": self.project.sites.first(),
            "project": self.project,
            "resource": self.ds_resource.resource,
            "created_by": author,
            "content": content,
            "status": Task.DONE,
        }

        if self.action:
            Task.objects.filter(pk=self.action.id).update(**action_data)
            return

        with transaction.atomic():
            self.action = Task.objects.create(**action_data)
            self.save()
