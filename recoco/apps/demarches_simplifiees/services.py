from typing import Any

from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource

from .models import DSResource


def find_ds_resource_for_project(
    project: Project, resource: Resource
) -> DSResource | None:
    if project.commune:
        return resource.dsresource_set.filter(
            departments=project.commune.department
        ).first()


def make_ds_data_from_project(
    project: Project, ds_resource: DSResource
) -> dict[str, Any]:

    ds_data: dict[str, Any] = {}

    for mapping_field in ds_resource.mapping_fields.exclude(
        project_lookup_key__isnull=True
    ):
        if value := project.get_from_lookup_key(
            lookup_key=mapping_field.project_lookup_key
        ):
            ds_data[mapping_field.field_id] = value

    return ds_data
