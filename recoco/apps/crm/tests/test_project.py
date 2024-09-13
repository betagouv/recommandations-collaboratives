import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from django.utils.text import capfirst, slugify
from model_bakery import baker
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects

from recoco.apps.home import models as home_models
from recoco.apps.onboarding import models as onboarding_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects import utils as projects_utils
from recoco.utils import login

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
def test_crm_project_details_available_for_staff(request, client, project):
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )

    url = reverse("crm-project-details", args=[project.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_crm_project_update_not_available_for_non_staff(request, client, project):
    url = reverse("crm-project-update", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_update_not_available_for_other_site(request, client, make_project):
    site = baker.make(site_models.Site)
    project = make_project(site=site)

    url = reverse("crm-project-update", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_update_available_for_staff(request, client, project):
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
def test_toggle_unauthorized_project_annotation(request, client, project):
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )

    url = reverse("crm-project-toggle-annotation", args=[project.id])
    data = {"tag": "a nice tag"}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    annotation = models.ProjectAnnotations.objects.first()
    assert annotation is None

    url = reverse("crm-project-details", args=[project.id])
    assertRedirects(response, url)


@pytest.mark.django_db
def test_toggle_missing_project_annotation(request, client, project):
    test_tag = "a nice tag"
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()
    site_config = baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )
    site_config.crm_available_tags.add(test_tag)

    url = reverse("crm-project-toggle-annotation", args=[project.id])
    data = {"tag": test_tag}

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data=data)

    annotation = models.ProjectAnnotations.objects.first()
    assert test_tag in annotation.tags.names()

    url = reverse("crm-project-details", args=[annotation.project.id])
    assertRedirects(response, url)


@pytest.mark.django_db
def test_toggle_on_project_annotation(request, client, project):
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()
    test_tag = "a nice tag"
    other_tag = "an other nice tag"
    site_config = baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )
    site_config.crm_available_tags.add(test_tag)
    site_config.crm_available_tags.add(other_tag)

    annotation = baker.make(models.ProjectAnnotations, site=site, project=project)
    detail_url = reverse("crm-project-details", args=[annotation.project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.get(detail_url)
        assert response.status_code == 200

        # unselected tag
        assertContains(
            response,
            f'id="checkbox-{slugify(test_tag)}" >',
        )
        assertContains(
            response,
            f'<label class="form-check-label" for="checkbox-{slugify(test_tag)}">{capfirst(test_tag)}</label>',
        )
        assertContains(
            response,
            f'id="checkbox-{slugify(other_tag)}" >',
        )
        assertContains(
            response,
            f'<label class="form-check-label" for="checkbox-{slugify(other_tag)}">{capfirst(other_tag)}</label>',
        )

        url = reverse("crm-project-toggle-annotation", args=[annotation.project.id])
        response = client.post(url, data={"tag": test_tag})
        updated = models.ProjectAnnotations.objects.first()
        assert test_tag in updated.tags.names()
        assertRedirects(response, detail_url)

        response = client.get(detail_url)
        assert response.status_code == 200
        # selected tag
        assertContains(
            response,
            f'id="checkbox-{slugify(test_tag)}" checked>',
        )
        # unselected tag
        assertContains(
            response,
            f'id="checkbox-{slugify(other_tag)}" >',
        )


@pytest.mark.django_db
def test_toggle_off_project_annotation(request, client, project):
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()
    test_tag = "a nice tag"
    other_tag = "an other nice tag"
    site_config = baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )
    site_config.crm_available_tags.add(test_tag)
    site_config.crm_available_tags.add(other_tag)

    annotation = baker.make(models.ProjectAnnotations, site=site, project=project)
    detail_url = reverse("crm-project-details", args=[annotation.project.id])

    data = {"tag": other_tag}
    annotation.tags.add(data["tag"])

    url = reverse("crm-project-toggle-annotation", args=[annotation.project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.get(detail_url)
        assert response.status_code == 200
        # unselected tag
        assertContains(
            response,
            f'id="checkbox-{slugify(test_tag)}" >',
        )
        assertContains(
            response,
            f'<label class="form-check-label" for="checkbox-{slugify(test_tag)}">{capfirst(test_tag)}',
        )
        # selected tag
        assertContains(
            response,
            f'id="checkbox-{slugify(other_tag)}" checked>',
        )
        assertContains(
            response,
            f'<label class="form-check-label" for="checkbox-{slugify(other_tag)}">{capfirst(other_tag)}',
        )

        response = client.post(url, data=data)

        updated = models.ProjectAnnotations.objects.first()
        assert data["tag"] not in updated.tags.names()

        url = reverse("crm-project-details", args=[annotation.project.id])
        assertRedirects(response, url)


#### Handover
@pytest.mark.django_db
def test_crm_project_handover_is_not_reachable_by_nonstaff(request, client, project):
    url = reverse("crm-project-handover", args=[project.id])

    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_handover_is_reachable(request, client, project):
    url = reverse("crm-project-handover", args=[project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_handover(request, client, project):
    url = reverse("crm-project-handover", args=[project.id])
    other_site = baker.make(
        site_models.Site, name="other site", configuration__accept_handover=True
    )
    john = baker.make(auth_models.User, first_name="John", last_name="DOE")
    projects_utils.assign_collaborator(john, project, is_owner=True)

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data={"site": other_site.pk})
        assert response.status_code == 302

    project.refresh_from_db()

    assert len(project.project_sites.all()) == 2


@pytest.mark.django_db
def test_crm_project_handover_on_existing_site(request, client, project):
    url = reverse("crm-project-handover", args=[project.id])

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data={"site": get_current_site(request).pk})
        assert response.status_code == 200

    project.refresh_from_db()

    assert len(project.project_sites.all()) == 1


@pytest.mark.django_db
def test_crm_project_handover_is_refused_if_not_authorized(request, client, project):
    url = reverse("crm-project-handover", args=[project.id])
    other_site = baker.make(
        site_models.Site, name="other site", configuration__accept_handover=False
    )

    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data={"site": other_site.pk})
        assert response.status_code == 200

    project.refresh_from_db()

    assert len(project.project_sites.all()) == 1


# eof
