from django.contrib.auth.models import User
from django.db import models, transaction
from model_utils.models import TimeStampedModel

from recoco.apps.geomatics.models import Department
from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.tasks.models import Task

from .choices import DSType
from .utils import hash_data


class DSResource(TimeStampedModel):
    name = models.CharField(max_length=255, unique=True)
    schema = models.JSONField(default=dict, null=True, blank=True)
    resource = models.ForeignKey(
        Resource, null=True, blank=True, on_delete=models.SET_NULL
    )
    type = models.CharField(
        max_length=50, choices=DSType.choices, default=DSType.DETR_DSIL
    )
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    field_mapping = models.JSONField(default=dict, null=True, blank=True)

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

    # FIXME: these 2 fields could be not nullable
    dossier_prefill_token = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)

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

    def update_or_create_action(self, created_by: User):
        # TODO: complete the action content
        content = f"[Lien vers la démarche simplifiée pré-remplie]({self.dossier_url})"

        action_data = {
            "site": self.project.sites.first(),
            "project": self.project,
            "resource": self.ds_resource.resource,
            "created_by": created_by,
            "content": content,
            "status": Task.DONE,
        }

        if self.action:
            Task.objects.filter(pk=self.action.id).update(**action_data)
            return

        with transaction.atomic():
            self.action = Task.objects.create(**action_data)
            self.save()
