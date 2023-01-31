# encoding: utf-8

"""
Tests for invite application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-04-20 10:11:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from . import api, models


@pytest.mark.django_db
def test_email_is_always_lowercased_on_invite():
    invited_email = "New@inVitEd.org"

    Recipe(
        models.Invite,
        email=invited_email,
    ).make()

    invite = models.Invite.objects.first()
    assert invite.email == invited_email.lower()


################################################################
# Invite API
################################################################
@pytest.mark.django_db
def test_invite_collaborator_api(request, client):
    current_site = get_current_site(request)

    invited_email = "new@invited.org"

    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        status="READY",
    )

    with login(client) as user:
        invite = api.invite_collaborator_on_project(
            current_site, project, "COLLABORATOR", invited_email, "hi", user
        )

    assert invite
    assert invite.inviter == user
    assert invite.site == current_site
    assert invite.project == project
    assert invite.email == invited_email


@pytest.mark.django_db
def test_invite_collaborator_twice_api(request, client):
    current_site = get_current_site(request)

    invited_email = "new@invited.org"

    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        status="READY",
    )

    with login(client) as user:
        invite1 = api.invite_collaborator_on_project(
            current_site, project, "COLLABORATOR", invited_email, "hi", user
        )

        invite2 = api.invite_collaborator_on_project(
            current_site, project, "COLLABORATOR", invited_email, "hi", user
        )

    assert invite1
    assert invite2 is False


@pytest.mark.django_db
def test_invite_collaborator_after_leaved_api(request, client):
    current_site = get_current_site(request)

    invited_email = "new@invited.org"

    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        status="READY",
    )

    Recipe(
        models.Invite,
        email=invited_email,
        site=current_site,
        project=project,
        accepted_on="2022-01-01",
    ).make()

    with login(client) as user:
        invite = api.invite_collaborator_on_project(
            current_site, project, "COLLABORATOR", invited_email, "hi", user
        )

    assert invite


################################################################
# Invite details
################################################################
@pytest.mark.django_db
def test_invite_available_for_everyone(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_invite_show_error_message_if_not_for_current_logged_in_user(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_does_not_match_existing_account(request, client):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite, site=get_current_site(request), email=invited.email
    ).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_for_logged_in_user(request, client):
    with login(client) as user:
        invite = Recipe(
            models.Invite, site=get_current_site(request), email=user.email
        ).make()
        url = reverse("invites-invite-details", args=[invite.pk])
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_redirects_anonyous_user_to_login(
    request, client
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite, site=get_current_site(request), email=invited.email
    ).make()

    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302


################################################################
# Invite accepts
################################################################
@pytest.mark.django_db
def test_accept_invite_returns_to_details_if_get(request, client):
    invite = Recipe(models.Invite, site=get_current_site(request)).make()
    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302
    assert invite.accepted_on is None


@pytest.mark.django_db
def test_accept_invite_matches_existing_account(request, client):
    with login(client) as user:
        invite = Recipe(
            models.Invite, site=get_current_site(request), email=user.email
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None


@pytest.mark.django_db
def test_accept_invite_as_switchtender_triggers_notification(request, client):
    current_site = get_current_site(request)

    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        projectmember_set=[membership],
        status="READY",
    )

    with login(client) as user:
        user.profile.sites.add(current_site)
        invite = Recipe(
            models.Invite,
            project=project,
            site=current_site,
            email=user.email,
            role="SWITCHTENDER",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    assert membership.member.notifications.count() == 1


@pytest.mark.django_db
def test_accept_invite_as_team_member_triggers_notification(request, client):
    current_site = get_current_site(request)

    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project = baker.make(
        projects_models.Project,
        sites=[current_site],
        projectmember_set=[membership],
        status="READY",
    )

    with login(client) as user:
        invite = Recipe(
            models.Invite,
            project=project,
            site=current_site,
            email=user.email,
            role="COLLABORATOR",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    assert membership.member.notifications.count() == 1


@pytest.mark.django_db
def test_user_cannot_access_member_invitation_for_someone_else(
    request,
    client,
):
    current_site = get_current_site(request)
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=current_site,
            email="whatever@wherever.com",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert current_site not in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_switchtender_with_matching_existing_account(
    request,
    client,
):
    current_site = get_current_site(request)
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=current_site,
            role="SWITCHTENDER",
            email=user.email,
            project__name="project",
            project__location="here",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user == invite.project.switchtenders_on_site.first().switchtender


@pytest.mark.django_db
def test_user_cannot_access_switchtender_invitation_for_someone_else(
    request,
    client,
):
    current_site = get_current_site(request)

    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        site=current_site,
        email=invited.email,
    ).make()

    with login(client, email="invited@here.tld") as user:
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert current_site not in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_matching_existing_account(
    request,
    client,
):
    current_site = get_current_site(request)
    with login(client, email="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            role="COLLABORATOR",
            site=current_site,
            email=user.email,
            project__name="project",
            project__location="here",
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_mismatched_existing_account(
    request,
    client,
):
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=get_current_site(request),
        email=invited.email,
    ).make()

    with login(client, email="invited@here.tld") as user:
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_anonymous_accepts_invite_with_existing_account_fails(
    request,
    client,
):
    current_site = get_current_site(request)
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
        email=invited.email,
    ).make()

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is None
    assert invite.project.members.count() == 0
    assert invite.project.switchtenders.count() == 0


@pytest.mark.django_db
def test_anonymous_accepts_invite_as_switchtender(
    request,
    client,
):
    current_site = get_current_site(request)
    invite = Recipe(
        models.Invite,
        role="SWITCHTENDER",
        site=current_site,
        email="a@new.one",
    ).make()

    data = {
        "first_name": "First",
        "last_name": "Last",
        "organization": "Some Organization",
        "position": "Doing Stuff",
    }

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url, data=data)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert invite.project.members.count() == 0
    assert invite.project.switchtenders_on_site.count() == 1

    user = auth_models.User.objects.get(email=invite.email)
    assert user.username == invite.email
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["organization"]
    assert user.profile.organization_position == data["position"]
    assert current_site in user.profile.sites.all()


@pytest.mark.django_db
def test_anonymous_accepts_invite_as_collaborator(
    request,
    client,
):
    current_site = get_current_site(request)
    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
        email="a@new.one",
    ).make()

    data = {
        "first_name": "First",
        "last_name": "Last",
        "organization": "Some Organization",
        "position": "Doing Stuff",
    }

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url, data=data)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert invite.project.members.count() == 1
    assert invite.project.switchtenders_on_site.count() == 0

    user = auth_models.User.objects.get(email=invite.email)
    assert user.username == invite.email
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["organization"]
    assert user.profile.organization_position == data["position"]
    assert current_site in user.profile.sites.all()


# eof
