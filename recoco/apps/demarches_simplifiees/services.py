import importlib
from pathlib import Path
from typing import Any

from django.conf import settings

from recoco.apps.projects.models import Project

from .choices import DSType
from .models import DSResource


def find_ds_resource_for_project(project: Project) -> DSResource | None:
    if not project.commune:
        return None

    return DSResource.objects.filter(
        type=DSType.DETR_DSIL, departments=project.commune.department
    ).first()


def make_ds_data_from_project(
    project: Project, ds_resource: DSResource
) -> dict[str, Any]:

    module_name = "{}.{}".format(
        str(
            Path(settings.DS_ADAPTERS_DIR).relative_to(settings.BASE_DIR.parent)
        ).replace("/", "."),
        ds_resource.number,
    )

    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return {}

    return module.make(project=project)
