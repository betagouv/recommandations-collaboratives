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
from django.utils import timezone
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertNotContains

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.home import models as home_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import assign_advisor, assign_collaborator
from recoco.utils import has_perm, login

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
def test_invite_collaborator_api(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited_email = "new@invited.org"

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
def test_invite_collaborator_twice_api(request, client, mailoutbox, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited_email = "new@invited.org"

    with login(client) as user:
        invite1 = api.invite_collaborator_on_project(
            current_site, project, "COLLABORATOR", invited_email, "hi", user
        )

        assert invite1
        assert len(mailoutbox) == 1

        with pytest.raises(api.InviteAlreadyInvitedException):
            api.invite_collaborator_on_project(
                current_site, project, "COLLABORATOR", invited_email, "hi", user
            )


@pytest.mark.django_db
def test_invite_collaborator_but_already_member(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    email = "invited@people.org"

    membership = baker.make(
        projects_models.ProjectMember,
        project=project,
        member__is_staff=False,
        member__username=email,
        member__email=email,
    )

    with login(client) as user:
        with pytest.raises(api.InviteAlreadyMemberException):
            api.invite_collaborator_on_project(
                current_site,
                project,
                "COLLABORATOR",
                membership.member.email,
                "hi",
                user,
            )


@pytest.mark.django_db
def test_invite_collaborator_after_leaved_api(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited_email = "new@invited.org"

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
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(models.Invite, site=current_site).make()
    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_invite_404_if_already_accepted(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    with login(client) as user:
        invite = baker.make(
            models.Invite, site=current_site, accepted_on=timezone.now()
        )
        invite.project.members.add(user, through_defaults={"is_owner": False})
        url = reverse("invites-invite-details", args=[invite.pk])
        response = client.get(url, follow=True)
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302
        assert last_url == reverse(
            "projects-project-detail-overview", args=(invite.project_id,)
        )


@pytest.mark.django_db
def test_invite_show_error_message_if_not_for_current_logged_in_user(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(models.Invite, site=current_site).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_does_not_match_existing_account(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(models.Invite, site=current_site, email=invited.email).make()
    url = reverse("invites-invite-details", args=[invite.pk])

    with login(client):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_for_logged_in_user(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(models.Invite, site=current_site, email=user.email).make()
        url = reverse("invites-invite-details", args=[invite.pk])
        response = client.get(url)

    assert response.status_code == 200
    assertNotContains(response, "Désolé")


@pytest.mark.django_db
def test_invite_matches_existing_account_redirects_anonyous_user_to_login(
    request, client
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invited = Recipe(
        auth_models.User, username="invited@example.com", email="invited@example.com"
    ).make()

    invite = Recipe(models.Invite, site=current_site, email=invited.email).make()

    url = reverse("invites-invite-details", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302


################################################################
# Invite accepts
################################################################
@pytest.mark.django_db
def test_accept_invite_returns_to_details_if_get(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(models.Invite, site=current_site).make()
    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302
    assert invite.accepted_on is None


@pytest.mark.django_db
def test_accept_invite_matches_existing_account(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite, project=project, site=current_site, email=user.email
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None


@pytest.mark.django_db
def test_accept_invite_as_switchtender_triggers_notification(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )
    project.projectmember_set.add(membership)

    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
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
def test_accept_invite_as_team_member_triggers_notification(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    membership = baker.make(
        projects_models.ProjectMember, member__is_staff=False, is_owner=True
    )

    project.projectmember_set.add(membership)

    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
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
    baker.make(home_models.SiteConfiguration, site=current_site)

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
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()
    assert not has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_advisor_with_matching_existing_account(
    request, client, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=current_site,
            role="SWITCHTENDER",
            email=user.email,
            project=project,
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    switchtending = invite.project.switchtender_sites.first()
    assert user == switchtending.switchtender
    assert switchtending.is_observer is False
    assert has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_observer_with_matching_existing_account(
    request, client, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            site=current_site,
            role="OBSERVER",
            email=user.email,
            project=project,
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    switchtending = invite.project.switchtender_sites.first()
    assert user == switchtending.switchtender
    assert switchtending.is_observer is True
    assert has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_user_cannot_access_switchtender_invitation_for_someone_else(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

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
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()
    assert not has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_matching_existing_account(
    request, client, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            role="COLLABORATOR",
            site=current_site,
            email=user.email,
            project=project,
        ).make()
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()
    assert has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_collaborator_with_mismatched_existing_account(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
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
    assert not has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_anonymous_accepts_invite_with_existing_account_fails(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited = Recipe(
        auth_models.User, username="invited@example.com", email="invited@example.com"
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
def test_anonymous_accepts_invite_as_switchtender(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(
        models.Invite,
        role="SWITCHTENDER",
        site=current_site,
        project=project,
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
    assert invite.project.switchtender_sites.count() == 1

    user = auth_models.User.objects.get(email=invite.email)
    assert user.username == invite.email
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["organization"]
    assert user.profile.organization_position == data["position"]
    assert current_site in user.profile.sites.all()
    assert has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_anonymous_accepts_invite_as_collaborator(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
        project=project,
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
    assert invite.project.switchtender_sites.count() == 0

    user = auth_models.User.objects.get(email=invite.email)
    assert user.username == invite.email
    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]
    assert user.profile.organization.name == data["organization"]
    assert user.profile.organization_position == data["position"]
    assert current_site in user.profile.sites.all()
    assert has_perm(user, "view_project", invite.project)


@pytest.mark.django_db
def test_accepting_invitation_assigns_organization_to_current_site(
    request, client, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        project=project,
        site=current_site,
        email="a@new.one",
    ).make()

    data = {
        "first_name": "First",
        "last_name": "Last",
        "organization": "New Organization",
        "position": "Doing Stuff",
    }

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url, data=data)

    assert response.status_code == 302

    orga = addressbook_models.Organization.on_site.first()
    assert orga.name == data["organization"]


@pytest.mark.django_db
def test_accepting_invitation_updates_organization_with_current_site(
    request, client, project
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
        project=project,
        email="a@new.one",
    ).make()

    data = {
        "first_name": "First",
        "last_name": "Last",
        "organization": "New Organization",
        "position": "Doing Stuff",
    }

    baker.make(addressbook_models.Organization, name=data["organization"])

    url = reverse("invites-invite-accept", args=[invite.pk])
    response = client.post(url, data=data)

    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_but_is_already_member(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            role="COLLABORATOR",
            site=current_site,
            email=user.email,
            project=project,
        ).make()
        assign_collaborator(user, invite.project, is_owner=False)

        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()


@pytest.mark.django_db
def test_logged_in_user_accepts_invite_but_is_already_advisor(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite,
            role="OBSERVER",
            site=current_site,
            email=user.email,
            project__name="project",
            project__location="here",
        ).make()
        assign_advisor(user, invite.project, current_site)

        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.accepted_on is not None
    assert current_site in user.profile.sites.all()
    assert user in invite.project.switchtenders.all()
    assert user not in invite.project.members.all()


# Refusing invitations
@pytest.mark.django_db
def test_refuse_invite_returns_to_details_if_get(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    invite = Recipe(models.Invite, site=current_site).make()
    url = reverse("invites-invite-refuse", args=[invite.pk])
    response = client.get(url)

    assert response.status_code == 302
    assert invite.refused_on is None


@pytest.mark.django_db
def test_reufse_invite_matches_existing_account(request, client, project):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)
    with login(client, email="invited@here.tld", username="invited@here.tld") as user:
        invite = Recipe(
            models.Invite, project=project, site=current_site, email=user.email
        ).make()
        url = reverse("invites-invite-refuse", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 302
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.refused_on is not None


@pytest.mark.django_db
def test_user_cannot_access_already_refused_invitation(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    with login(client, email="invited@here.tld") as user:
        invite = baker.make(
            models.Invite,
            site=current_site,
            email=user.email,
            refused_on=timezone.now(),
        )
        url = reverse("invites-invite-accept", args=[invite.pk])
        response = client.post(url, follow=True)
        last_url, status_code = response.redirect_chain[-1]
        assert status_code == 302
        assert last_url == reverse(
            "projects-project-detail-overview", args=(invite.project_id,)
        )


@pytest.mark.django_db
def test_anonymous_refuses_invite_with_existing_account_fails(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited = Recipe(
        auth_models.User, username="invited@example.com", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        role="COLLABORATOR",
        site=current_site,
        email=invited.email,
    ).make()

    url = reverse("invites-invite-refuse", args=[invite.pk])
    response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.refused_on is None
    assert invite.project.members.count() == 0
    assert invite.project.switchtenders.count() == 0


@pytest.mark.django_db
def test_user_cannot_refuse_invitation_for_someone_else(
    request,
    client,
):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    invited = Recipe(
        auth_models.User, username="invited", email="invited@example.com"
    ).make()

    invite = Recipe(
        models.Invite,
        site=current_site,
        email=invited.email,
    ).make()

    with login(client, email="invited@here.tld") as user:
        url = reverse("invites-invite-refuse", args=[invite.pk])
        response = client.post(url)

    assert response.status_code == 403
    invite = models.Invite.on_site.get(pk=invite.pk)
    assert invite.refused_on is None
    assert current_site in user.profile.sites.all()
    assert user not in invite.project.members.all()
    assert user not in invite.project.switchtenders.all()
    assert not has_perm(user, "view_project", invite.project)


# Managers
@pytest.mark.django_db
def test_manager_active_filter(request, project):
    current_site = get_current_site(request)

    pending_invite = baker.make(
        models.Invite,
        role="COLLABORATOR",
        accepted_on=None,
        site=current_site,
        project=project,
        email="a@new.one",
    )

    # accepted one
    baker.make(
        models.Invite,
        role="COLLABORATOR",
        accepted_on=timezone.now(),
        refused_on=None,
        site=current_site,
        project=project,
        email="another@new.one",
    )

    # refused one
    baker.make(
        models.Invite,
        role="COLLABORATOR",
        accepted_on=None,
        refused_on=timezone.now(),
        site=current_site,
        project=project,
        email="yetanother@new.one",
    )

    assert models.Invite.objects.count() == 3
    assert models.Invite.objects.pending().count() == 1

    assert models.Invite.objects.pending().first() == pending_invite


# eof
