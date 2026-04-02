from copy import deepcopy as copy

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils.functional import cached_property
from model_utils.models import TimeStampedModel

from recoco.apps.geomatics.models import Department
from recoco.apps.home.models import SiteConfiguration
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import Question, QuestionSet

from .utils import MappingField, project_mapping_fields


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
    def fields(self) -> list[MappingField]:
        # FIXME: trouver la liste des champs communs DS, hors schema
        fields = [
            MappingField(
                id="identite_prenom",
                label="Prénom",
            ),
            MappingField(
                id="identite_nom",
                label="Nom",
            ),
        ]
        try:
            fields += [
                MappingField(
                    id="champ_" + field.get("id").replace("==", ""),
                    label=field.get("label"),
                    options=field.get("options"),
                )
                for field in self.schema["revision"]["champDescriptors"]
            ]
        except KeyError:
            pass
        return fields


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
        verbose_name = "Mapping configuration"
        verbose_name_plural = "Mapping configurations"
        ordering = ["-created"]
        unique_together = ["ds_resource", "site"]
        indexes = [
            models.Index(fields=["enabled"]),
        ]

    def __str__(self) -> str:
        return f"{self.ds_resource} - {self.site}"

    @property
    def ds_fields(self) -> list[MappingField]:
        return self.ds_resource.fields

    @property
    def indexed_ds_fields(self) -> dict[str, MappingField]:
        return {field.id: field for field in self.ds_fields}

    @cached_property
    def recoco_fields(self) -> list[MappingField]:
        fields = copy(project_mapping_fields)

        if site_configuration := SiteConfiguration.objects.filter(
            site=self.site
        ).first():
            if survey := site_configuration.project_survey:
                for question in Question.objects.filter(
                    question_set__in=QuestionSet.objects.filter(
                        survey_id=survey.id
                    ).values("id")
                ):
                    fields += [
                        MappingField(
                            id=f"edl.{question.slug}",
                            label=question.text_short,
                            lookup=question.slug,
                        ),
                        MappingField(
                            id=f"edl.{question.slug}.comment",
                            label=question.text_short,
                            lookup=f"{question.slug}.comment",
                        ),
                    ]
        return fields

    @cached_property
    def indexed_recoco_fields(self) -> dict[str, MappingField]:
        return {field.id: field for field in self.recoco_fields}
