# encoding: utf-8

"""
Tests for project application / administration

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-12-26 11:54:56 CEST
"""

import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.utils import login

from .. import models

##############################################################
# General cases
##############################################################


@pytest.mark.django_db
def test_invite_email_for_existing_user_uses_autologin(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="own@er.fr",
        member__username="own@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    collab = baker.make(auth.User, username="collaborator@example.com")

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": collab.username, "message": "noice"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 302

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_email_cannot_be_added_twice(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="own@er.fr",
        member__username="own@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)
        assert response.status_code == 302

        response = client.post(url, data=data)
        assert response.status_code == 302

    assert invites_models.Invite.objects.count() == 1
    invite = invites_models.Invite.objects.first()
    assert invite.email == data["email"]


##############################################################
# Collectivity Member invites
##############################################################


@pytest.mark.django_db
def test_non_staff_cannot_invite_collectivity_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-access-collectivity-invite", args=[project.id])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_assigned_switchtender_can_invite_collectivity_to_project(request, client):
    project = baker.make(
        models.Project, sites=[get_current_site(request)], projectmember_set=[]
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "test@example.com", "message": "hey"}

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_regional_actor_can_invite_collectivity_to_project(request, client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    current_site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[current_site],
        projectmember_set=[],
        commune=commune,
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "test@example.com"}

    with login(client, groups=["switchtender"]) as user:
        user.profile.sites.add(current_site)
        user.profile.departments.set([project.commune.department.pk])

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_can_invite_collectivity_member_if_not_draft(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="own@er.fr",
        member__username="own@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 302

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_cannot_invite_email_to_project_if_draft(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="user@staff.fr",
        member__username="user@staff.fr",
    )
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="DRAFT",
    ).make()

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 403


##############################################################
# Advisors invites
##############################################################


@pytest.mark.django_db
def test_user_cannot_invite_collectivity_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-access-collectivity-invite", args=[project.id])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_assigned_switchtender_can_invite_advisor_to_project(request, client):
    current_site = get_current_site(request)

    project = baker.make(models.Project, sites=[current_site], projectmember_set=[])

    url = reverse("projects-project-access-advisor-invite", args=[project.id])
    data = {"email": "test@example.com", "message": "hey"}

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_regional_actor_can_invite_advisor_to_project(request, client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    current_site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[current_site],
        projectmember_set=[],
        commune=commune,
    )

    url = reverse("projects-project-access-advisor-invite", args=[project.id])
    data = {"email": "test@example.com"}

    with login(client, groups=["switchtender"]) as user:
        user.profile.sites.add(current_site)
        user.profile.departments.set([project.commune.department.pk])

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_collectivity_member_cannot_invite_an_advisor(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="us@er.fr",
        member__username="us@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-project-access-advisor-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 403

    assert invites_models.Invite.on_site.count() == 0


##################################################
# Revocation
##################################################


@pytest.mark.django_db
def test_invitation_revocation(request, client):
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=get_current_site(request),
        project=project,
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client, is_staff=True):
        response = client.post(url, data=data)
        assert response.status_code == 302
        assert "login" not in response.url

    assert invites_models.Invite.objects.count() == 0
