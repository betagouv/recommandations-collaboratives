import logging
from typing import Any
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib.sites.models import Site

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import Answer, Session
from recoco.apps.tasks.models import Task

from .exceptions import DSAPIError
from .models import DSMapping, DSResource
from .utils import MappingField

logger = logging.getLogger(__name__)


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
        # retrieve the DS field from the DS schema
        ds_field = ds_mapping.indexed_ds_fields.get(ds_field_id)
        if ds_field is None:
            logger.error(
                f"DS field {ds_field_id} not found in DS schema for resource {ds_resource.name}"
            )
            continue

        ds_value = None

        # iterate over the mapping items
        for mapping_item in mapping_items:
            conditions_ok: bool = True

            # check conditions are met for the current mapping item
            for condition in mapping_item.get("conditions", []):
                if not resolve_mapping_value(
                    value=condition.get("value"),
                    recoco_field=ds_mapping.indexed_recoco_fields.get(
                        condition.get("value")
                    ),
                    session=session,
                    conditions=condition.get("tags"),
                ):
                    conditions_ok = False
                    break

            # if conditions are met, resolve the mapping value
            if conditions_ok:
                ds_value = resolve_mapping_value(
                    value=mapping_item.get("value"),
                    ds_field=ds_field,
                    recoco_field=ds_mapping.indexed_recoco_fields.get(
                        mapping_item.get("value")
                    ),
                    project=project,
                    session=session,
                )

        if ds_value:
            data[ds_field_id] = ds_value

    return data


def resolve_mapping_value(
    value: str,
    ds_field: MappingField | None = None,
    recoco_field: MappingField | None = None,
    project: Project | None = None,
    session: Session | None = None,
    conditions: list[str] | None = None,
) -> Any | None:
    # raw value expected
    if value.startswith("raw["):
        return value[4:-1]

    # DS field option value expected
    if value.startswith("option[") and ds_field:
        try:
            option = int(value[7:-1])
            return ds_field.options[option]
        except (ValueError, IndexError):
            return None

    # resolve from Recoco project fields
    if value.startswith("project.") and project and recoco_field:
        return resolve_project_lookup(project=project, lookup=recoco_field.lookup)

    # resolve from Recoco EDL fields
    if value.startswith("edl.") and session and recoco_field:
        return resolve_edl_lookup(
            session=session, lookup=recoco_field.lookup, conditions=conditions
        )


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
    session: Session, lookup: str, conditions: list[str] | None = None
) -> Any | None:
    _take_comment = False
    if lookup.endswith(".comment"):
        lookup = lookup[:-8]
        _take_comment = True

    answer = Answer.objects.filter(session_id=session.id, question__slug=lookup).first()
    if answer is None:
        return None

    if conditions:
        answer_tags = [tag.strip() for tag in answer.signals.split(",") if tag]
        if not all(tag in answer_tags for tag in conditions):
            return None

    return answer.comment if _take_comment else answer.formatted_value


def load_ds_resource_schema(ds_resource_id: int):
    try:
        ds_resource = DSResource.objects.get(id=ds_resource_id)
    except DSResource.DoesNotExist:
        return

    if ds_resource.schema and len(ds_resource.schema) > 0:
        return

    resp = requests.get(
        url=urljoin(ds_resource.preremplir_url, "schema"),
        timeout=30,
    )
    if resp.status_code != 200:
        raise DSAPIError(
            f"Failed to load schema for the DS resource {ds_resource.name}",
            status_code=resp.status_code,
        )

    ds_resource.schema = resp.json()
    ds_resource.save()


def create_ds_prefill_link(recommendation_id: int):
    try:
        recommendation = Task.objects.select_related(
            "project__commune__department"
        ).get(id=recommendation_id)
    except Task.DoesNotExist:
        return

    if recommendation.resource is None:
        return

    ds_resource: DSResource = find_ds_resource_for_project(
        project=recommendation.project,
        resource=recommendation.resource,
    )
    if ds_resource is None:
        return

    content = make_ds_data_from_project(
        site=recommendation.site,
        project=recommendation.project,
        ds_resource=ds_resource,
    )
    resp = requests.post(
        url=urljoin(
            settings.DS_API_BASE_URL, f"demarches/{ds_resource.number}/dossiers"
        ),
        json=content,
        timeout=30,
    )
    if resp.status_code != 201:
        raise DSAPIError(
            f"Failed to generate a prefill url for the DS resource {ds_resource.name}",
            status_code=resp.status_code,
        )

    return resp.json()["dossier_url"]
