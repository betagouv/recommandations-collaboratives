from typing import Any

from recoco.apps.projects.models import Project


def make(project: Project) -> dict[str, Any]:
    return {
        "champ_Q2hhbXAtMzc3ODEy": project.name,
    }