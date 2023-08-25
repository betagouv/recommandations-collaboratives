import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects

from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from .. import models

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
    assertNotContains(response, unexpected)


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
    assertNotContains(response, unexpected)


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
    assertNotContains(response, unexpected)
    expected = reverse("crm-project-details", args=[inactive.id])
    assertContains(response, expected)


@pytest.mark.django_db
def test_crm_project_list_filters_by_project_name(request, client):
    site = get_current_site(request)
    expected = baker.make(projects_models.Project, sites=[site], name="expected")
    unexpected = baker.make(projects_models.Project, sites=[site], name="unexpected")

    url = reverse("crm-project-list") + f"?query={expected.name}"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-project-details", args=[expected.id])
    assertContains(response, expected)
    unexpected = reverse("crm-project-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


@pytest.mark.django_db
def test_crm_project_list_filters_by_commune_name(request, client):
    site = get_current_site(request)
    expected = baker.make(
        projects_models.Project, sites=[site], commune__name="recherchée"
    )
    unexpected = baker.make(
        projects_models.Project, sites=[site], commune__name="ignorée"
    )

    url = reverse("crm-project-list") + f"?query={expected.commune.name}"
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200

    expected = reverse("crm-project-details", args=[expected.id])
    assertContains(response, expected)
    unexpected = reverse("crm-project-details", args=[unexpected.id])
    assertNotContains(response, unexpected)


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
    data = {"statistics": False}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert response.status_code == 200

    updated = projects_models.Project.objects.first()
    assert updated.exclude_stats is True


@pytest.mark.django_db
def test_crm_project_update_property_muted(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site], muted=False)

    url = reverse("crm-project-update", args=[project.id])
    data = {"notifications": False}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    assert response.status_code == 200

    updated = projects_models.Project.objects.first()
    assert updated.muted is True


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


@pytest.mark.django_db
def test_crm_search_by_project_name_on_current_site(request, client):
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


@pytest.mark.django_db
def test_crm_search_by_user_name_on_current_site(request, client):
    current_site = get_current_site(request)
    other_site = baker.make(site_models.Site)

    john = baker.make(auth_models.User, first_name="John", last_name="DOE")
    john.profile.sites.add(current_site)

    jane = baker.make(auth_models.User, first_name="Jane", last_name="DOE")
    jane.profile.sites.add(other_site)

    data = {"query": "doe"}

    url = reverse("crm-search")
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 200
    assertContains(response, john.first_name)
    assertNotContains(response, jane.first_name)


########################################################################
# project annotations
########################################################################


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
