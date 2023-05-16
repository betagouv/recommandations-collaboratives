import collections

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import get_group_for_site, login

from .. import models, views

########################################################################
# list
########################################################################


@pytest.mark.django_db
def test_crm_project_list_not_available_for_non_staff(client):
    url = reverse("crm-project-list")
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_list_contains_site_projects(request, client):
    site = get_current_site(request)
    expected = baker.make(projects_models.Project, sites=[site])
    other = baker.make(site_models.Site)
    unexpected = baker.make(projects_models.Project, sites=[other])

    url = reverse("crm-project-list")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-project-details", args=[expected.id])
    assertContains(response, expected)
    unexpected = reverse("crm-project-details", args=[unexpected.id])
    assertContains(response, unexpected)


@pytest.mark.django_db
def test_crm_project_list_filters_active_ones(request, client):
    site = get_current_site(request)
    active = baker.make(projects_models.Project, sites=[site])
    inactive = baker.make(
        projects_models.Project,
        deleted=timezone.now(),
        sites=[site],
    )

    url = reverse("crm-project-list")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-project-details", args=[active.id])
    assertContains(response, expected)
    unexpected = reverse("crm-project-details", args=[inactive.id])
    assertContains(response, unexpected)


@pytest.mark.django_db
def test_crm_project_list_filters_inactive_ones(request, client):
    site = get_current_site(request)
    active = baker.make(projects_models.Project, sites=[site])
    inactive = baker.make(
        projects_models.Project,
        deleted=timezone.now(),
        sites=[site],
    )

    url = reverse("crm-project-list") + "?inactive=True"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    unexpected = reverse("crm-project-details", args=[active.id])
    assertContains(response, unexpected)
    expected = reverse("crm-project-details", args=[inactive.id])
    assertContains(response, expected)


@pytest.mark.django_db
def test_crm_project_list_filters_by_name(request, client):
    site = get_current_site(request)
    expected = baker.make(projects_models.Project, sites=[site])
    unexpected = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-list") + f"?name={expected.name[5:15]}"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-project-details", args=[expected.id])
    assertContains(response, expected)
    unexpected = reverse("crm-project-details", args=[unexpected.id])
    assertContains(response, unexpected)


########################################################################
# details
########################################################################


@pytest.mark.django_db
def test_crm_project_details_available_for_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-details", args=[project.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_crm_project_update_not_available_for_non_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-update", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_update_not_available_for_other_site(request, client):
    site = baker.make(site_models.Site)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-update", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_update_available_for_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-update", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_update_property_exclude_stats(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site], exclude_stats=False)

    url = reverse("crm-project-update", args=[project.id])
    data = {"exclude_stats": True}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert response.status_code == 302

    updated = projects_models.Project.objects.first()
    assert updated.exclude_stats


@pytest.mark.django_db
def test_crm_project_update_property_muted(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site], muted=False)

    url = reverse("crm-project-update", args=[project.id])
    data = {"muted": True}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert response.status_code == 302

    updated = projects_models.Project.objects.first()
    assert updated.muted


#
# delete


@pytest.mark.django_db
def test_crm_project_delete_not_available_for_non_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-delete", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_delete_not_available_for_staff_other_site(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-delete", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_delete_available_for_staff_on_site(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-delete", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_delete(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-delete", args=[project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    updated = projects_models.Project.deleted_on_site.first()
    assert updated.id == project.id


#
# undelete


@pytest.mark.django_db
def test_crm_project_undelete_not_available_for_non_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-undelete", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_undelete_not_available_for_staff_other_site(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-undelete", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_undelete_available_for_staff_on_site(request, client):
    site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        deleted=timezone.now(),
        sites=[site],
    )

    url = reverse("crm-project-undelete", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_undelete(request, client):
    site = get_current_site(request)
    project = baker.make(
        projects_models.Project,
        sites=[site],
        deleted=timezone.now(),
    )

    url = reverse("crm-project-undelete", args=[project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    updated = projects_models.Project.objects.first()
    assert updated.id == project.id


#
# project create note


@pytest.mark.django_db
def test_crm_project_create_note_not_accessible_for_non_staff(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_create_note_not_accessible_other_site(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)

    project = baker.make(projects_models.Project, sites=[other])

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_create_note_accessible_for_staff(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)

    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_create_note(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

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


#
# project annotations


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


# eof
