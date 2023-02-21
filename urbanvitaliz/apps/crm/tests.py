import pytest
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from . import models


@pytest.mark.django_db
def test_crm_organization_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-organization-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_crm_user_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-user-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_crm_project_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-project-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_crm_organization_available_for_staff(client):
    org = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-details", args=[org.pk])
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_available_for_staff(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-details", args=[project.pk])
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_available_for_staff(client):
    user = baker.make(auth_models.User)

    url = reverse("crm-user-details", args=[user.pk])
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_create_note(client):
    project = baker.make(projects_models.Project)

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-project-note-create", args=[project.pk])
    with login(client, is_staff=True):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


########################################################################
# Dashboard
########################################################################


@pytest.mark.django_db
def test_site_dashboard_not_available_for_non_switchtender_users(client):
    url = reverse("crm-site-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_site_dashboard_available_for_switchtender_users(client):
    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)
    assert response.status_code == 200
