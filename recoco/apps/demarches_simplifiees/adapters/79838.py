from typing import Any

from recoco.apps.projects.models import Project


def make(project: Project) -> dict[str, Any]:
    d = {
        # "identite_prenom": project.first_name,
        # "identite_nom": project.last_name,
        "champ_Q2hhbXAtMzUyMTg1Mg": project.name,
    }

    if owner := project.owner:
        d.update(
            {
                "champ_Q2hhbXAtMzUyMTg0Ng": f"{owner.last_name} {owner.first_name}",
                "champ_Q2hhbXAtMzUyMTg0OA": owner.email,
                "champ_Q2hhbXAtMzUyMTg0Nw": owner.profile.organization_position,
                "champ_Q2hhbXAtMzUyMTg0OQ": owner.profile.phone_no.as_international,
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
