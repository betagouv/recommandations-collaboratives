from typing import Any

from recoco.apps.projects.models import Project

from .models import DemarcheSimplifiee


def find_ds_for_project(project: Project) -> DemarcheSimplifiee | None:
    # TODO: find the DS that match with the project
    return None


def build_ds_data_from_project(
    project: Project, demarche: DemarcheSimplifiee
) -> dict[str, Any]:
    # TODO: build the data to send to DS API
    return {}
