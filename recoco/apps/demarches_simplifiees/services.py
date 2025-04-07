from typing import Any

from django.contrib.sites.models import Site

from recoco.apps.home.models import SiteConfiguration
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


def _get_session(site: Site, project: Project) -> Session | None:
    if site_configuration := SiteConfiguration.objects.filter(site=site).first():
        if survey := site_configuration.project_survey:
            return Session.objects.filter(
                project_id=project.id, survey_id=survey.id
            ).first()


def make_ds_data_from_project(
    site: Site, project: Project, ds_resource: DSResource
) -> dict[str, Any]:
    data = {}

    ds_mapping = DSMapping.objects.filter(
        ds_resource_id=ds_resource.id, site_id=site.id, enabled=True
    ).first()
    if ds_mapping is None:
        return data

    session = _get_session(site=site, project=project)

    for ds_field_id, mapping_items in ds_mapping.mapping.items():
        ds_value = None

        for mapping_item in mapping_items:
            value = mapping_item.get("value")

            if value.startswith("raw["):
                ds_value = value[4:-1]
                continue

            recoco_field = ds_mapping.indexed_recoco_fields.get(value)
            if recoco_field is None:
                continue

            if value.startswith("project."):
                if res := resolve_project_lookup(
                    project=project, lookup=recoco_field.lookup
                ):
                    ds_value = res
                continue

            if value.startswith("edl.") and session:
                if res := resolve_edl_lookup(
                    session=session,
                    lookup=recoco_field.lookup,
                    condition=mapping_item.get("condition", []),
                ):
                    ds_value = res
                continue

        if ds_value is not None:
            data[ds_field_id] = ds_value

    return data


def _recursive_get_attr(obj: Any, lookup: str) -> Any | None:
    parts = lookup.split(".")

    current_attr = parts[0]
    if not hasattr(obj, current_attr):
        return None

    value = getattr(obj, current_attr)

    remaining_lookup = ".".join(parts[1:])
    if not remaining_lookup:
        return value

    return _recursive_get_attr(value, remaining_lookup)


def resolve_project_lookup(project: Project, lookup: str) -> Any | None:
    return _recursive_get_attr(project, lookup)


def resolve_edl_lookup(
    session: Session, lookup: str, condition: list[str] = None
) -> Any | None:
    _take_comment = False
    if lookup.endswith(".comment"):
        lookup = lookup[:-8]
        _take_comment = True

    answer = Answer.objects.filter(session_id=session.id, question__slug=lookup).first()
    if answer is None:
        return None

    if condition:
        answer_tags = [tag.strip() for tag in answer.signals.split(",") if tag]
        if not all(tag in answer_tags for tag in condition):
            return None

    return answer.comment if _take_comment else answer.formatted_value
