import collections

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from pytest_django.asserts import assertContains, assertNotContains
from django.conf import settings
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from . import models, views


@pytest.mark.django_db
def test_crm_organization_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-organization-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-user-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-project-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_toggle_missing_project_annotation(request, client):
    site = get_current_site(request)

    project = baker.make(models.projects_models.Project, sites=[site])

    url = reverse("crm-project-toggle-annotation", args=[project.id])
    data = {"tag": "a nice tag"}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    annotation = models.ProjectAnnotations.objects.first()
    assert data["tag"] in annotation.tags.names()

    url = reverse("crm-project-details", args=[annotation.project.id])
    assertRedirects(response, url)


@pytest.mark.django_db
def test_toggle_on_project_annotation(request, client):
    site = get_current_site(request)

    project = baker.make(models.projects_models.Project, sites=[site])
    annotation = baker.make(models.ProjectAnnotations, site=site, project=project)

    url = reverse("crm-project-toggle-annotation", args=[annotation.project.id])
    data = {"tag": "a nice tag"}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    updated = models.ProjectAnnotations.objects.first()
    assert data["tag"] in updated.tags.names()

    url = reverse("crm-project-details", args=[annotation.project.id])
    assertRedirects(response, url)


@pytest.mark.django_db
def test_toggle_off_project_annotation(request, client):
    site = get_current_site(request)

    project = baker.make(models.projects_models.Project, sites=[site])
    annotation = baker.make(models.ProjectAnnotations, site=site, project=project)

    data = {"tag": "précédent"}
    annotation.tags.add(data["tag"])

    url = reverse("crm-project-toggle-annotation", args=[annotation.project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    updated = models.ProjectAnnotations.objects.first()
    assert data["tag"] not in updated.tags.names()

    url = reverse("crm-project-details", args=[annotation.project.id])
    assertRedirects(response, url)


@pytest.mark.django_db
def test_crm_organization_available_for_staff(client):
    org = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-details", args=[org.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_available_for_staff(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-details", args=[project.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_available_for_staff(client):
    user = baker.make(auth_models.User)

    url = reverse("crm-user-details", args=[user.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_create_note(client):
    project = baker.make(projects_models.Project)

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-project-note-create", args=[project.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


@pytest.mark.django_db
def test_crm_search(request, client):
    current_site = get_current_site(request)
    second_site = baker.make(site_models.Site)

    project_on_site = baker.make(
        projects_models.Project, name="Mon petit canard", sites=[current_site]
    )
    project_no_site = baker.make(projects_models.Project, name="Mon petit poussin")
    project_another_site = baker.make(
        projects_models.Project, name="Mon petit poulet", sites=[second_site]
    )

    data = {"query": "petit"}

    url = reverse("crm-search")
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 200
    assertContains(response, project_on_site.name)
    assertNotContains(response, project_no_site.name)
    assertNotContains(response, project_another_site.name)


########################################################################
# Dashboard
########################################################################


@pytest.mark.django_db
def test_site_dashboard_not_available_for_non_staff_users(client):
    url = reverse("crm-site-dashboard")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_site_dashboard_available_for_staff_users(client):
    url = reverse("crm-site-dashboard")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)
    assert response.status_code == 200


########################################################################
# tag cloud
########################################################################


@pytest.mark.django_db
def test_compute_tag_cloud():
    site = baker.make(site_models.Site)
    project_annotation = baker.make(models.ProjectAnnotations, site=site)
    project_annotation.tags.add("tag0", "tag1")
    note = baker.make(models.Note, site=site, related=project_annotation.project)
    note.tags.add("tag0", "tag2")
    tags = views.compute_tag_occurences(site)
    assert tags == collections.OrderedDict(
        {
            "tag0": 2,
            "tag1": 1,
            "tag2": 1,
        }
    )


# eof
