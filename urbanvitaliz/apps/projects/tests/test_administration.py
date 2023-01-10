# encoding: utf-8

"""
Tests for project application / administration

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-12-26 11:54:56 CEST
"""


import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertRedirects)
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.utils import login

from .. import models

########################################################################
# Project administration
########################################################################


@pytest.mark.django_db
def test_project_admin_not_available_for_non_staff_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-administration", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_project_admin_not_available_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-administration", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_project_admin_wo_commune_and_redirect(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-administration", args=[project.id])
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "description": "a project description",
        "impediment": "some impediment",
    }

    with login(client, groups=["switchtender"], is_staff=True) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    project = models.Project.on_site.get(id=project.id)
    assert project.name == data["name"]
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_project_admin_with_commune(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=commune
    ).make()
    url = reverse("projects-project-administration", args=[project.id])

    with login(client, groups=["switchtender"], is_staff=True) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)

    assertContains(response, "<form")
    assertContains(response, commune.postal)


@pytest.mark.django_db
def test_project_admin_update_commune(request, client):
    old_commune = Recipe(
        geomatics.Commune, name="old town", postal="12345", insee="1234"
    ).make()
    new_commune = Recipe(
        geomatics.Commune, name="new town", postal="7890", insee="789"
    ).make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=old_commune
    ).make()
    url = reverse("projects-project-administration", args=[project.id])

    data = {
        "name": "a project",
        "location": "some place",
        "description": "a project description",
        "postcode": new_commune.postal,
        "insee": new_commune.insee,
    }

    with login(client, groups=["switchtender"], is_staff=True) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    assert response.status_code == 302

    project = models.Project.objects.get(id=project.pk)
    assert project.commune == new_commune


#####################################################################
# Collectivity ACLs
#####################################################################


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, membership.member.email],
    )

    with login(client, groups=["switchtender"], is_staff=True) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert membership in project.projectmember_set.all()

    update_url = reverse("projects-project-administration", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_collectivity_member_cannot_remove_member_from_project(request, client):
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
        member__username="owner@ab.fr",
    )
    collab_membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="coll@ab.fr",
        member__username="coll@ab.fr",
    )
    project = Recipe(
        models.Project,
        projectmember_set=[owner_membership, collab_membership],
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collab_membership.member.email],
    )

    with login(client, user=owner_membership.member):
        response = client.post(url)

    assert response.status_code == 302
    assert "login" in response.url

    project = models.Project.on_site.get(id=project.id)
    assert collab_membership.member in project.members.all()


@pytest.mark.django_db
def test_advisor_cannot_remove_collectivity_member_from_project(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, membership.member.email],
    )

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url)

    assert response.status_code == 302
    assert "login" in response.url

    project = models.Project.on_site.get(id=project.id)
    assert membership in project.projectmember_set.all()


@pytest.mark.django_db
def test_non_staff_cannot_remove_collectivity_member_from_project(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="user@staff.fr",
        member__username="user@staff.fr",
    )
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    ).make()

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, membership.member.email],
    )

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 302
    assert "login" in response.url


#####################################################################
# Adivsor ACLs
#####################################################################


@pytest.mark.django_db
def test_collectivity_member_cannot_remove_advisor_from_project(request, client):
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
        member__username="owner@ab.fr",
    )
    advisor = baker.make(
        models.ProjectSwitchtender,
        switchtender__is_staff=False,
        switchtender__email="ad@visor.fr",
        switchtender__username="ad@visor.fr",
        site=get_current_site(request),
    )
    project = Recipe(
        models.Project,
        projectmember_set=[owner_membership],
        switchtenders_on_site=[advisor],
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, advisor.switchtender.email],
    )

    with login(client, user=owner_membership.member):
        response = client.post(url)

    assert response.status_code == 302
    assert "login" in response.url

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders_on_site.all()


@pytest.mark.django_db
def test_advisor_cannot_remove_advisor_from_project(request, client):
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
        member__username="owner@ab.fr",
    )
    active_advisor = baker.make(
        models.ProjectSwitchtender,
        switchtender__is_staff=False,
        switchtender__email="me@visor.fr",
        switchtender__username="me@visor.fr",
        site=get_current_site(request),
    )

    advisor = baker.make(
        models.ProjectSwitchtender,
        switchtender__is_staff=False,
        switchtender__email="ad@visor.fr",
        switchtender__username="ad@visor.fr",
        site=get_current_site(request),
    )
    project = Recipe(
        models.Project,
        projectmember_set=[owner_membership],
        switchtenders_on_site=[advisor, active_advisor],
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.switchtender.email],
    )

    with login(client, user=active_advisor.switchtender):
        response = client.post(url)

    assert response.status_code == 302
    assert "login" in response.url

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders_on_site.all()
