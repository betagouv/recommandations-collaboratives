import logging
import re
from typing import Any

from django.contrib.sites.models import Site

from recoco.apps.home.models import SiteConfiguration
from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource
from recoco.apps.survey.models import Answer, Session

from .models import DSMapping, DSResource

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

    for ds_field_id, recoco_field_id in ds_mapping.mapping.items():
        if recoco_field_id.startswith("raw["):
            data[ds_field_id] = recoco_field_id[4:-1]
            continue

        if recoco_field_id.startswith("eval["):
            expression = recoco_field_id[5:-1]

            for var in re.findall(r"\$\((.*?)\)", expression):
                recoco_field = ds_mapping.indexed_recoco_fields.get(var)
                if recoco_field is None:
                    continue

                if var.startswith("project."):
                    if res := resolve_project_lookup(project, recoco_field.lookup):
                        expression = expression.replace(f"$({var})", str(res))

                elif var.startswith("edl.") and session:
                    if res := resolve_edl_lookup(session, recoco_field.lookup):
                        expression = expression.replace(f"$({var})", str(res))

            try:
                data[ds_field_id] = eval(expression)  # noqa: S307
            except Exception:
                logger.error(f"DS mapping: unable to evaluate expression: {expression}")

        recoco_field = ds_mapping.indexed_recoco_fields.get(recoco_field_id)
        if recoco_field is None:
            continue

        if recoco_field_id.startswith("project."):
            if res := resolve_project_lookup(project, recoco_field.lookup):
                data[ds_field_id] = res
            continue

        if recoco_field_id.startswith("edl.") and session:
            if res := resolve_edl_lookup(session, recoco_field.lookup):
                data[ds_field_id] = res
            continue

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


def resolve_edl_lookup(session: Session, lookup: str) -> Any | None:
    _take_comment = False
    if lookup.endswith(".comment"):
        lookup = lookup[:-8]
        _take_comment = True

    if answer := Answer.objects.filter(
        session_id=session.id, question__slug=lookup
    ).first():
        return answer.comment if _take_comment else answer.formatted_value
