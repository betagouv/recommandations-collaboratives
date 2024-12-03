from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel

from recoco.apps.geomatics.models import Department
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
    departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name="demarches_simplifiees",
        verbose_name="Départements concernés",
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

    @property
    def fields(self) -> list[dict[str, str]]:
        try:
            return [
                {
                    "field_id": f"champ_{field.get('id')}",
                    "field_label": field.get("label"),
                    "field_options": field.get("options", []),
                }
                for field in self.schema["revision"]["champDescriptors"]
            ]
        except KeyError:
            return []

    @property
    def preremplir_url(self) -> str:
        return f"{settings.DS_BASE_URL}/preremplir/{self.name}"


class DSMappingField(TimeStampedModel):
    ds_resource = models.ForeignKey(
        DSResource,
        on_delete=models.CASCADE,
        related_name="mapping_fields",
    )

    field_id = models.CharField(max_length=255)
    field_label = models.CharField(max_length=255)
    field_options = models.JSONField(default=list)

    project_lookup_key = models.CharField(max_length=255, null=True, blank=True)

    enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ["ds_resource", "field_id"]
        verbose_name = "Mapping de champ"
        verbose_name_plural = "Mappings de champ"
        ordering = ["field_label"]

    def __str__(self) -> str:
        return self.field_label


class DSFolder(TimeStampedModel):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )
    ds_resource = models.ForeignKey(
        DSResource,
        on_delete=models.CASCADE,
    )

    dossier_id = models.CharField(max_length=255)
    dossier_url = models.URLField()
    dossier_number = models.IntegerField()
    dossier_prefill_token = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    content = models.JSONField()
    content_hash = models.CharField(max_length=255)

    recommendation = models.OneToOneField(
        Task,
        related_name="ds_folder",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Dossier pré-rempli"
        verbose_name_plural = "Dossiers pré-remplis"
        ordering = ["-created"]
        unique_together = ["project", "ds_resource"]

    def __str__(self) -> str:
        return self.dossier_id

    def save(self, *args, **kwargs):
        self.content_hash = hash_data(dict(self.content))
        super().save(*args, **kwargs)

    @property
    def prefilled_count(self) -> int:
        return len(self.content)
