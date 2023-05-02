import collections

import pytest
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertRedirects)
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from . import filters, models, views

########################################################################
# organization
########################################################################


@pytest.mark.django_db
def test_crm_organization_not_available_for_non_staff_logged_users(client):
    url = reverse("crm-organization-details", args=[1])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


########################################################################
# users
########################################################################


@pytest.mark.django_db
def test_crm_user_list_not_available_for_non_staff(client):
    url = reverse("crm-user-list")
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_list_contains_only_selected_user(request, client):
    site = get_current_site(request)

    expected = baker.make(auth_models.User)
    expected.profile.sites.add(site)

    unexpected = baker.make(auth_models.User)
    unexpected.profile.sites.add(site)

    url = reverse("crm-user-list") + f"?username={expected.username[:10]}"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[expected.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_contains_only_active_user(request, client):
    site = get_current_site(request)

    active = baker.make(auth_models.User, is_active=True)
    active.profile.sites.add(site)

    inactive = baker.make(auth_models.User, is_active=False)
    inactive.profile.sites.add(site)

    url = reverse("crm-user-list") + f"?active=true"

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[active.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[inactive.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_user_list_contains_only_selected_role(request, client):
    site = get_current_site(request)

    staff = baker.make(auth_models.User)
    staff.profile.sites.add(site)
    gstaff = auth_models.Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)

    advisor = baker.make(auth_models.User)
    advisor.profile.sites.add(site)
    gadvisor = auth_models.Group.objects.get(name="example_com_advisor")
    advisor.groups.add(gadvisor)

    a_user = baker.make(auth_models.User)
    a_user.profile.sites.add(site)

    url = reverse("crm-user-list") + f"?role=2"  # role 2 is staff

    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-user-details", args=[staff.id])
    assertContains(response, expected)

    unexpected = reverse("crm-user-details", args=[advisor.id])
    assertNotContains(response, unexpected)

    unexpected = reverse("crm-user-details", args=[a_user.id])
    assertNotContains(response, unexpected)


########################################################################
# project
########################################################################


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
