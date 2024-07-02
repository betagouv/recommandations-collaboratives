import requests
from celery import shared_task
from django.conf import settings

from recoco.apps.projects.models import Project

from .exceptions import DSAPIError
from .models import DSFolder, DSResource
from .services import build_ds_data_from_project, find_ds_resource_for_project
from .utils import hash_data


@shared_task(
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=300,
    autoretry_for=(DSAPIError,),
)
def load_ds_resource_schema(ds_resource_id: int):
    try:
        ds_resource = DSResource.objects.get(id=ds_resource_id)
    except DSResource.DoesNotExist:
        return

    if len(ds_resource.schema) > 0:
        return

    resp = requests.get(
        url=f"{settings.DS_BASE_URL}/preremplir/{ds_resource.name}/schema",
        timeout=30,
    )
    if resp.status_code != 200:
        raise DSAPIError(
            f"Failed to load schema for the DS resource {ds_resource.name}",
            status_code=resp.status_code,
        )

    ds_resource.schema = resp.json()
    ds_resource.save()


@shared_task(
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
    retry_backoff_max=300,
    autoretry_for=(DSAPIError,),
)
def update_or_create_ds_action(project_id: int):
    try:
        project = Project.objects.select_related("commune__department").get(
            id=project_id
        )
    except Project.DoesNotExist:
        # TODO: handle error
        return

    ds_resource: DSResource = find_ds_resource_for_project(project=project)
    if ds_resource is None or ds_resource.number is None:
        return

    content = build_ds_data_from_project(
        project=project,
        ds_resource=ds_resource,
    )
    if not len(content):
        return

    if DSFolder.objects.filter(
        project=project,
        ds_resource=ds_resource,
        content_hash=hash_data(content),
    ).exists():
        return

    resp = requests.post(
        url=f"{settings.DS_API_BASE_URL}/demarches/{ds_resource.number}/dossiers",
        json=content,
        timeout=30,
    )
    if resp.status_code != 201:
        raise DSAPIError(
            f"Failed to create a DS folder for the DS resource {ds_resource.name}",
            status_code=resp.status_code,
        )

    ds_folder, _ = DSFolder.objects.update_or_create(
        project=project,
        ds_resource=ds_resource,
        defaults={
            "content": content,
            **resp.json(),
        },
    )
    ds_folder.update_or_create_action(created_by=project.owner)
