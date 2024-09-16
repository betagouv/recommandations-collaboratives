from typing import Any

from recoco.apps.projects.models import Project


def make(project: Project) -> dict[str, Any]:
    d = {
        "champ_Q2hhbXAtMjk3MTQ0NA": project.name,
        "champ_Q2hhbXAtMzI5MzY1Mw": project.description,
    }

    if len(project.first_name) and len(project.last_name):
        d.update(
            {
                "champ_Q2hhbXAtMjkzNDM5Mw": f"{project.first_name} {project.last_name}",
            }
        )

    if len(project.phone):
        d.update(
            {
                "champ_Q2hhbXAtMjkzNDQwMQ": project.phone,
            }
        )

    return d
