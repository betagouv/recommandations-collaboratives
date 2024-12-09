from typing import Any

from django.contrib.sites.models import Site

from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import Answer, Session

from .models import DSMapping, DSResource


def find_ds_resource_for_project(
    project: Project, resource: Resource
) -> DSResource | None:
    if project.commune:
        return resource.dsresource_set.filter(
            departments=project.commune.department
        ).first()


def make_ds_data_from_project(
    site: Site, project: Project, ds_resource: DSResource
) -> dict[str, Any]:
    data = {}

    ds_mapping = DSMapping.objects.filter(
        ds_resource_id=ds_resource.id, site_id=site.id
    ).first()
    if ds_mapping is None:
        return data

    if survey := site.configuration.project_survey:
        session = Session.objects.filter(
            project_id=project.id, survey_id=survey.id
        ).first()

        for ds_field, lookup_key in ds_mapping.mapping.items():
            if lookup_key.startswith("project."):
                data[ds_field] = getattr(project, lookup_key.replace("project.", ""))
                continue

            if lookup_key.startswith("edl."):
                question_slug = lookup_key.replace("edl.", "")

                answer: Answer = Answer.objects.filter(
                    session_id=session.id, question__slug=question_slug
                ).first()
                if answer:
                    data[ds_field] = answer.formatted_value

    return data
