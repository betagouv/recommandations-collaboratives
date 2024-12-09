from dataclasses import dataclass

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from model_utils.models import TimeStampedModel

from recoco.apps.geomatics.models import Department
from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import Question, QuestionSet, Survey
from recoco.apps.tasks.models import Task

from .utils import hash_data


@dataclass
class Field:
    id: str
    label: str
    options: list[str] | None = None


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
    def preremplir_url(self) -> str:
        return f"{settings.DS_BASE_URL}/preremplir/{self.name}"

    @property
    def fields(self) -> list[Field]:
        try:
            return [
                Field(
                    id="champ_" + field.get("id").replace("==", ""),
                    label=field.get("label"),
                    options=field.get("options"),
                )
                for field in self.schema["revision"]["champDescriptors"]
            ]
        except KeyError:
            return []


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


class DSMappingManager(models.Manager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().select_related("ds_resource", "site")


class DSMapping(TimeStampedModel):
    ds_resource = models.ForeignKey(
        DSResource,
        on_delete=models.CASCADE,
        related_name="ds_mappings",
    )

    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="ds_mappings",
    )

    enabled = models.BooleanField(default=True)

    mapping = models.JSONField(default=dict, blank=True)

    objects = DSMappingManager()

    class Meta:
        verbose_name = "Mapping"
        verbose_name_plural = "Mappings"
        ordering = ["-created"]
        unique_together = ["ds_resource", "site"]

    def __str__(self) -> str:
        return f"{self.ds_resource} - {self.site}"

    @property
    def ds_fields(self) -> list[Field]:
        return self.ds_resource.fields

    @property
    def lookup_fields(self) -> list[Field]:
        lookup_fields = []

        for project_field in Project._meta.get_fields(include_parents=False):
            if project_field.name in (
                "description",
                "first_name",
                "last_name",
                "name",
                "phone",
            ):
                lookup_fields.append(
                    Field(
                        id="project." + project_field.name,
                        label=project_field.verbose_name,
                    )
                )

        survey_ids = Survey.objects.filter(site_id=self.site_id).values("id")
        question_set_ids = QuestionSet.objects.filter(survey__in=survey_ids).values(
            "id"
        )
        for question in Question.objects.filter(question_set__in=question_set_ids):
            lookup_fields += [
                Field(id=f"edl.{question.slug}", label=question.text_short),
                Field(
                    id=f"edl.{question.slug}.comment",
                    label=f"{question.text_short} (COMMENTAIRE)",
                ),
            ]

        return lookup_fields
