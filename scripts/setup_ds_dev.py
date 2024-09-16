from django.contrib.sites.models import Site

from recoco.apps.demarches_simplifiees.choices import DSType
from recoco.apps.demarches_simplifiees.models import DSResource
from recoco.apps.demarches_simplifiees.tasks import (
    load_ds_resource_schema,
    update_or_create_ds_folder,
)
from recoco.apps.geomatics.models import Department
from recoco.apps.projects.models import Project
from recoco.apps.resources.models import Resource


def _detr_resource() -> Resource:
    return Resource.objects.get(pk=69)


def _mec_site() -> Site:
    return Site.objects.filter(
        domain="monespacecollectivite.incubateur.anct.gouv.fr"
    ).first()


def _project_in_57() -> Project:
    return (
        Project.objects.filter(sites=_mec_site(), commune__department__code="57")
        .order_by("-created_on")
        .first()
    )


def update_detr_resource():
    print(">> Attach the DETR resource to the MEC site.")

    detr_resource = _detr_resource()
    detr_resource.sites.add(_mec_site())


def setup_ds_resources():
    print(">> Create a DSResource for the DETR DSIL 2024 in Moselle.")

    ds_resource, created = DSResource.objects.update_or_create(
        name="demande-de-subvention-detr-dsil-2024-en-moselle",
        defaults={
            "resource": _detr_resource(),
            "type": DSType.DETR_DSIL,
        },
    )
    if created:
        # add department 57
        ds_resource.departments.add(Department.objects.get(code="57"))
        # load the DS schema (automatically done when you use celery async tasks)
        load_ds_resource_schema.delay(ds_resource.id)


def setup_ds_folder():
    project = _project_in_57()

    print(f">> Update or ceate a DSFolder for the project {project.id}.")

    reco = (
        project.tasks.filter(resource=_detr_resource()).order_by("-created_on").first()
    )
    if reco is None:
        print(
            f">> No DETR recommendation found for the project {project.id}, please add one manually."
        )
        return

    # create a ds folder attached to this reco (automatically done when you use celery async tasks)
    update_or_create_ds_folder.delay(recommendation_id=reco.id)


assert _detr_resource(), "Resource DETR not found."  # nosec
assert _mec_site(), "Site MEC not found."  # nosec
assert _project_in_57(), "No project in dpt 57 found."  # nosec

update_detr_resource()
setup_ds_resources()
setup_ds_folder()
