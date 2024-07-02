from typing import Any

from recoco.apps.projects.models import Project

from .choices import DSType
from .models import DSResource


def find_ds_resource_for_project(project: Project) -> DSResource | None:
    if not project.commune:
        return None

    return DSResource.objects.filter(
        type=DSType.DETR_DSIL, department=project.commune.department
    ).first()


def build_ds_data_from_project(
    project: Project, ds_resource: DSResource
) -> dict[str, Any]:
    data = {}
    for ds_field_name, lookup in ds_resource.field_mapping.items():
        value = _resolve_lookup(project=project, lookup=lookup)
        if value is not None:
            data[ds_field_name] = value
    return data


def _resolve_lookup(project: Project, lookup: str) -> str | None:
    lookup_parts = lookup.split("__")
    if len(lookup_parts) == 1:
        return getattr(project, lookup)

    # TODO: implement the lookup resolution mechanism

    return None
