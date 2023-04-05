# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-17 12:33:33 CEST
"""

import django.core.mail
import pytest
from django import forms
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.urls import reverse
from guardian.shortcuts import assign_perm, remove_perm
from model_bakery import baker
from pytest_django.asserts import assertRedirects
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.projects.utils import assign_collaborator
from urbanvitaliz.utils import login

from . import adapters, models, utils


########################################################################
# utility functions
########################################################################


@pytest.mark.django_db
def test_get_current_site_sender_with_configuration(request):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    site_config = baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    sender = utils.get_current_site_sender()

    assert site_config.sender_email in sender
    assert site_config.sender_name in sender


@pytest.mark.django_db
def test_get_current_site_sender_without_configuration(request):
    sender = utils.get_current_site_sender()
    assert sender == settings.DEFAULT_FROM_EMAIL


################################################
# signup with sites
################################################


@pytest.mark.django_db
def test_create_user_assign_current_site_via_allauth(client, request):
    site = get_current_site(request)
    data = {
        "first_name": "Test",
        "last_name": "test",
        "organization": "test",
        "organization_position": "test",
        "email": "kkkd@kdkdk.fr",
        "phone_no": "0303003033",
        "password1": "6t2dCLGjNFTBuRv",
        "password2": "6t2dCLGjNFTBuRv",
    }
    response = client.post(reverse("account_signup"), data)
    assert response.status_code == 302

    user = auth_models.User.objects.get(email=data["email"])

    assert len(user.profile.sites.all()) == 1
    assert site in user.profile.sites.all()


#################################################
# create new user hook for magicauth
#################################################
@pytest.mark.django_db
def test_create_user_assign_current_site_via_magicauth(client, request):
    site = get_current_site(request)
    data = {
        "email": "kkkd@kdkdk.fr",
    }
    response = client.post(reverse("magicauth-login"), data)
    assert response.status_code == 302

    user = auth_models.User.objects.get(email=data["email"])

    assert len(user.profile.sites.all()) == 1
    assert site in user.profile.sites.all()


@pytest.mark.django_db
def test_create_user_with_proper_email(request):
    adapter = adapters.UVMagicauthAdapter()
    email = "new.user@example.com"
    adapter.email_unknown_callback(request, email, None)

    user = auth_models.User.objects.get(email=email)

    assert user.email == email
    assert user.username == email
    assert user.profile


@pytest.mark.django_db
def test_create_user_fails_with_missing_email(request):
    adapter = adapters.UVMagicauthAdapter()
    email = None
    with pytest.raises(forms.ValidationError):
        adapter.email_unknown_callback(request, email, None)


@pytest.mark.django_db
def test_create_user_fails_for_known_email(request):
    adapter = adapters.UVMagicauthAdapter()
    email = "known.user@example.com"
    baker.make(auth_models.User, username=email)
    with pytest.raises(IntegrityError):
        adapter.email_unknown_callback(request, email, None)


#
# seding message to team


@pytest.mark.django_db
def test_user_can_access_contact_form(client):
    url = reverse("home-contact") + "?next=/"
    response = client.get(url)

    assert b"<form " in response.content


@pytest.mark.django_db
def test_non_logged_user_can_send_message_to_team(mocker, client):
    mocker.patch("django.core.mail.send_mail")

    data = {
        "subject": "a subject",
        "content": "some content",
        "name": "john",
        "email": "jdoe@example.com",
    }
    url = reverse("home-contact") + "?next=/"
    response = client.post(url, data=data)

    content = data["content"] + "\n\nfrom: john jdoe@example.com\nsource: "

    django.core.mail.send_mail.assert_called_once_with(
        subject=data["subject"],
        message=content,
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )

    assertRedirects(response, "/")


@pytest.mark.django_db
def test_logged_user_can_send_message_to_team(mocker, client):
    mocker.patch("django.core.mail.send_mail")

    data = {"subject": "a subject", "content": "some content"}
    url = reverse("home-contact") + "?next=/"
    with login(client, is_staff=False) as user:
        response = client.post(url, data=data)

    content = data["content"] + f"\n\nfrom: {user.email}\nsource: "

    django.core.mail.send_mail.assert_called_once_with(
        subject=data["subject"],
        message=content,
        from_email=settings.EMAIL_FROM,
        recipient_list=settings.TEAM_EMAILS,
        fail_silently=True,
    )

    assertRedirects(response, "/")


########################################################################
# Login routing based on user profile
########################################################################
@pytest.mark.django_db
def test_project_owner_is_sent_to_action_page_on_login(request, client):
    url = reverse("login-redirect")
    project = baker.make(
        projects_models.Project,
        sites=[get_current_site(request)],
    )

    with login(client) as user:
        assign_collaborator(user, project, is_owner=True)
        response = client.get(url)

    assert response.status_code == 302
    project_action_url = reverse("projects-project-detail-actions", args=(project.pk,))
    assertRedirects(response, project_action_url)


@pytest.mark.django_db
def test_logged_in_user_is_sent_to_home_on_login(client):
    url = reverse("login-redirect")
    with login(client):
        response = client.get(url)
    assert response.status_code == 302
    assertRedirects(response, "/")


@pytest.mark.django_db
def test_switchtender_is_sent_to_project_list_on_login(client):
    url = reverse("login-redirect")
    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)
    assert response.status_code == 302
    list_url = reverse("projects-project-list")
    assert response.url == list_url


########################################################################
# Statistics
########################################################################


@pytest.mark.django_db
def test_user_can_access_stats(client):
    url = reverse("statistics")
    response = client.get(url)
    assert response.status_code == 200


#######################################################################
# Static pages
#######################################################################


@pytest.mark.django_db
def test_user_can_access_methodology(client):
    url = reverse("methodology")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_access_whoweare(client):
    url = reverse("whoweare")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_user_can_access_followus(client):
    url = reverse("followus")
    response = client.get(url)
    assert response.status_code == 200


################################################################
# guardian
################################################################


@pytest.mark.django_db
def test_guardian_supports_assign_for_user_with_site_framework(client, request):
    """Test usage of assign_perm for User"""
    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    with settings.SITE_ID.override(site1.pk):
        perm = assign_perm("add_project", user, project)
        assert perm.site == get_current_site(request)

        user_has_perm = user.has_perm("projects.add_project", project)
        assert user_has_perm is True

    with settings.SITE_ID.override(site2.pk):
        user_has_perm = user.has_perm("projects.add_project", project)
        assert user_has_perm is False


@pytest.mark.django_db
def test_guardian_supports_assign_for_group_with_site_framework(client, request):
    """Test usage of assign_perm for Group"""
    group = baker.make(auth_models.Group)
    user = baker.make(auth_models.User, groups=[group])
    project = baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    with settings.SITE_ID.override(site1.pk):
        group_perm = assign_perm("add_project", group, project)
        assert group_perm.site == get_current_site(request)

        user_has_perm = user.has_perm("projects.add_project", project)
        assert user_has_perm is True

    with settings.SITE_ID.override(site2.pk):
        user_has_perm = user.has_perm("projects.add_project", project)
        assert user_has_perm is False


@pytest.mark.django_db
def test_guardian_supports_bulk_assign_users_with_site_framework(client, request):
    baker.make(auth_models.User)
    baker.make(auth_models.User)
    project = baker.make(projects_models.Project)

    users = auth_models.User.objects.all()
    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    with settings.SITE_ID.override(site1.pk):
        perms = assign_perm("add_project", users, project)
        for perm in perms:
            assert perm.site == get_current_site(request)

        for user in users.all():
            assert user.has_perm("projects.add_project", project)

    with settings.SITE_ID.override(site2.pk):
        for user in users.all():
            assert not user.has_perm("projects.add_project", project)


@pytest.mark.django_db
def test_guardian_supports_bulk_assign_groups_with_site_framework(client, request):
    baker.make(auth_models.Group)
    baker.make(auth_models.Group)

    project = baker.make(projects_models.Project)

    groups = auth_models.Group.objects.all()

    site1 = baker.make(Site, pk=1)

    with settings.SITE_ID.override(site1.pk):
        perms = assign_perm("add_project", groups, project)
        for perm in perms:
            assert perm.site == get_current_site(request)


@pytest.mark.django_db
def test_guardian_supports_assigning_perms_to_two_different_sites(client, request):
    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    with settings.SITE_ID.override(site1.pk):
        assign_perm("add_project", user, project)

    with settings.SITE_ID.override(site2.pk):
        assign_perm("add_project", user, project)


@pytest.mark.django_db
def test_guardian_supports_remove_perm_with_site_framework(client, request):
    user = baker.make(auth_models.User)
    project = baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    with settings.SITE_ID.override(site1.pk):
        assign_perm("add_project", user, project)

    with settings.SITE_ID.override(site2.pk):
        assign_perm("add_project", user, project)

    with settings.SITE_ID.override(site1.pk):
        remove_perm("add_project", user, project)
        assert not user.has_perm("add_project", project)

    with settings.SITE_ID.override(site2.pk):
        assert user.has_perm("add_project", project)


@pytest.mark.django_db
def test_guardian_supports_remove_bulk_perm_for_user_with_site_framework(
    client, request
):
    user = baker.make(auth_models.User)
    baker.make(projects_models.Project)
    baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    projects = projects_models.Project.objects.all()

    with settings.SITE_ID.override(site1.pk):
        assign_perm("add_project", user, projects)

    with settings.SITE_ID.override(site2.pk):
        assign_perm("add_project", user, projects)

    with settings.SITE_ID.override(site1.pk):
        remove_perm("add_project", user, projects)
        for project in projects:
            assert not user.has_perm("add_project", project)

    with settings.SITE_ID.override(site2.pk):
        for project in projects:
            assert user.has_perm("add_project", project)


@pytest.mark.django_db
def test_guardian_supports_remove_bulk_perm_for_group_with_site_framework(
    client, request
):
    group = baker.make(auth_models.Group)
    user = baker.make(auth_models.User, groups=[group])
    baker.make(projects_models.Project)
    baker.make(projects_models.Project)

    site1 = baker.make(Site, pk=1)
    site2 = baker.make(Site, pk=2)

    projects = projects_models.Project.objects.all()

    with settings.SITE_ID.override(site1.pk):
        assign_perm("add_project", group, projects)

    with settings.SITE_ID.override(site2.pk):
        assign_perm("add_project", group, projects)

    with settings.SITE_ID.override(site1.pk):
        remove_perm("add_project", group, projects)
        for project in projects:
            assert not user.has_perm("add_project", project)

    with settings.SITE_ID.override(site2.pk):
        for project in projects:
            assert user.has_perm("add_project", project)


@pytest.mark.django_db
def test_make_new_site_fails_for_existing_domain(client):
    before = models.SiteConfiguration.objects.count()

    site = utils.make_new_site("Example", "example.com", "sender@example.com", "Sender")

    assert site is None
    assert models.SiteConfiguration.objects.count() == before


@pytest.mark.django_db
def test_make_new_site(client):
    site = utils.make_new_site(
        "New example", "new-example.com", "sender@example.com", "Sender"
    )

    assert site
    assert models.SiteConfiguration.objects.filter(site=site).count() == 1

    for name in (
        "new_example_com_staff",
        "new_example_com_advisor",
        "new_example_com_admin",
    ):
        assert auth_models.Group.objects.get(name=name)


#######################################################################
# Signals
#######################################################################


@pytest.mark.django_db
def test_user_signin_should_be_logged(request, client):
    with login(client) as user:
        assert user.actor_actions.count() == 1


@pytest.mark.django_db
def test_user_signin_shouldnt_be_logged_if_hijacked(request, client):
    hijacked = baker.make(auth_models.User, username="hijacked")

    with login(client, username="hijacker", is_staff=True):
        url = reverse("hijack:acquire")
        response = client.post(url, data={"user_pk": hijacked.pk})

    assert response.status_code == 302
    assert hijacked.actor_actions.count() == 0


# eof
