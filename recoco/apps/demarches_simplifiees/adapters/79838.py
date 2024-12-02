from typing import Any

from recoco.apps.projects.models import Project


def make(project: Project) -> dict[str, Any]:
    d = {
        "identite_prenom": project.first_name,
        "identite_nom": project.last_name,
        "champ_Q2hhbXAtMzUyMTg1Mg": project.name,
        "champ_Q2hhbXAtMzUyMTg0Nw": "",  # Fonction du référent
    }

    if len(project.first_name) and len(project.last_name):
        d.update(
            {
                "champ_Q2hhbXAtMzUyMTg0Ng": f"{project.last_name} {project.first_name}",
            }
        )

    if referrer := project.owner:
        d.update(
            {
                "champ_Q2hhbXAtMzUyMTg0OA": referrer.email,
                "champ_Q2hhbXAtMzUyMTg0Nw": referrer.organization_position,
                "champ_Q2hhbXAtMzUyMTg0OQ": referrer.phone_no,
            }
        )

    if commune := project.commune:
        d.update(
            {
                "champ_Q2hhbXAtMzUzNTIxMA": commune.insee,
                "champ_Q2hhbXAtMzUyMDc0NA": [commune.postal],
                "champ_Q2hhbXAtMzUyMDc3OA": commune.department.code,
                "champ_Q2hhbXAtMzUyMDc4MA": commune.department.region.code,
            }
        )

    return d
