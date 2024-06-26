import requests
from celery import shared_task
from django.conf import settings

from recoco.apps.projects.models import Project

from .models import DemarcheSimplifiee, DossierPreRempli
from .services import build_ds_data_from_project, find_ds_for_project

# https://doc.demarches-simplifiees.fr/pour-aller-plus-loin/api-de-preremplissage#preremplissage-en-post


# TODO: handle task retry
@shared_task
def call_ds_api_preremplir(project_id: int):
    try:
        project = Project.objects.get(id=project_id)
    except Project.DoesNotExist:
        # TODO: handle error
        return

    demarche: DemarcheSimplifiee = find_ds_for_project(project=project)
    if demarche is None:
        return

    resp = requests.post(
        url=f"{settings.DS_API_BASE_URL}/demarches/{demarche.ds_id}/preremplir",
        json=build_ds_data_from_project(
            project=project,
            demarche=demarche,
        ),
        timeout=30,
    )
    if resp.status_code != 200:
        # TODO: handle error
        pass

    DossierPreRempli.objects.create(
        project=project,
        demarche=demarche,
        **resp.json(),
    )
