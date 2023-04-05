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
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import Recipe
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.utils import login

from .. import models
from ..utils import assign_advisor, assign_collaborator

##############################################################
# General cases
##############################################################


@pytest.mark.django_db
def test_invite_email_for_existing_user_uses_autologin(request, client):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    )

    collab = baker.make(auth.User, username="collaborator@example.com")

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": collab.username, "message": "noice"}

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
        response = client.post(url, data=data)

    assert response.status_code == 302

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_email_cannot_be_added_twice(request, client):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
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
def test_lambda_user_cannot_invite_collaborator_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-access-collectivity-invite", args=[project.id])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_assigned_advisor_can_invite_collaborator_to_project(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site], projectmember_set=[])

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "test@example.com", "message": "hey"}

    with login(client) as user:
        assign_advisor(user, project, site)

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_regional_actor_can_invite_collaborator_to_project(request, client):
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

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)
        user.profile.departments.set([project.commune.department.pk])

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_staff_can_invite_collaborator_to_project(request, client):
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

    with login(client, groups=["example_com_staff"]) as user:
        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_can_invite_collaborator_member_if_not_draft(request, client):
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
        #        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-project-access-collectivity-invite", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
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
def test_assigned_advisor_can_invite_advisor_to_project(request, client):
    current_site = get_current_site(request)

    project = baker.make(models.Project, sites=[current_site], projectmember_set=[])

    url = reverse("projects-project-access-advisor-invite", args=[project.id])
    data = {"email": "test@example.com", "message": "hey"}

    with login(client) as user:
        assign_advisor(user, project, current_site)

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

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)
        user.profile.departments.set([project.commune.department.pk])

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_staff_can_invite_advisor_to_project(request, client):
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

    with login(client, groups=["example_com_staff"]) as user:
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


########################################################################
# Revoke collaborator invitations
########################################################################


@pytest.mark.django_db
def test_staff_cannot_revoke_accepted_invitation(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    invite = Recipe(
        invites_models.Invite,
        project=project,
        accepted_on=timezone.now(),
        site=get_current_site(request),
    ).make()

    url = reverse(
        "projects-project-access-revoke-invite",
        args=[project.id, invite.pk],
    )

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 404

    assert invites_models.Invite.on_site.count() == 1


@pytest.mark.django_db
def test_unprivileged_user_cannot_revoke_invitation(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    invite = Recipe(
        invites_models.Invite,
        site=get_current_site(request),
        project=project,
    ).make()

    url = reverse(
        "projects-project-access-revoke-invite",
        args=[project.id, invite.pk],
    )

    with login(client):
        response = client.post(url)

    assert response.status_code == 403

    assert invites_models.Invite.on_site.first() == invite


@pytest.mark.django_db
def test_collaborator_can_revoke_collaborator_invitation(request, client):
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
        role="COLLABORATOR",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert "login" not in response.url

    assert invites_models.Invite.objects.count() == 0


@pytest.mark.django_db
def test_advisor_can_revoke_collaborator_invitation(request, client):
    site = get_current_site(request)
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="COLLABORATOR",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client) as user:
        assign_advisor(user, project, site=site)
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert "login" not in response.url

    assert invites_models.Invite.objects.count() == 0


@pytest.mark.django_db
def test_staff_can_revoke_collaborator_invitation(request, client):
    site = get_current_site(request)
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="COLLABORATOR",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client, groups=["example_com_staff"]) as user:
        response = client.post(url, data=data)

    assert response.status_code == 302
    assert "login" not in response.url

    assert invites_models.Invite.objects.count() == 0


########################################################################
# Revoke advisor invitations
########################################################################


@pytest.mark.django_db
def test_collaborator_cannot_revoke_advisor_invitation(request, client):
    site = get_current_site(request)
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="SWITCHTENDER",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url, data=data)

    assert response.status_code == 403

    assert invites_models.Invite.objects.first() == invite


@pytest.mark.django_db
def test_advisor_cannot_revoke_other_advisor_invitation(request, client):
    site = get_current_site(request)
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="SWITCHTENDER",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client) as user:
        assign_advisor(user, project, site=site)
        response = client.post(url, data=data)

    assert response.status_code == 403

    assert invites_models.Invite.objects.count() == 1


@pytest.mark.django_db
def test_staff_can_revoke_advisor_invitation(request, client):
    site = get_current_site(request)
    invited_email = "invite@party.com"
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="SWITCHTENDER",
        email=invited_email,
    )

    url = reverse("projects-project-access-revoke-invite", args=[project.id, invite.pk])
    data = {"email": invited_email}

    with login(client, groups=["example_com_staff"]) as user:
        response = client.post(url, data=data)

    assert response.status_code == 302

    assert invites_models.Invite.objects.count() == 0


# eof
