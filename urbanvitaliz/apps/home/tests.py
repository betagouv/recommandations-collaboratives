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
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.db.utils import IntegrityError
from django.urls import reverse
from model_bakery import baker
from pytest_django.asserts import assertRedirects
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from . import adapters, models, utils


####
# utils
####
def test_get_current_site_sender_with_configuration(request):
    current_site = get_current_site(request)
    site_config = baker.make(models.SiteConfiguration, site=current_site)

    sender = utils.get_current_site_sender()

    assert site_config.sender_email in sender
    assert site_config.sender_name in sender


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

    user = auth.User.objects.first()

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

    user = auth.User.objects.first()

    assert len(user.profile.sites.all()) == 1
    assert site in user.profile.sites.all()


@pytest.mark.django_db
def test_create_user_with_proper_email(request):
    adapter = adapters.UVMagicauthAdapter()
    email = "new.user@example.com"
    adapter.email_unknown_callback(request, email, None)

    user = auth.User.objects.first()

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
    baker.make(auth.User, username=email)
    with pytest.raises(IntegrityError):
        adapter.email_unknown_callback(request, email, None)


#
# seding message to team


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
    membership = baker.make(projects_models.ProjectMember, is_owner=True)
    project = baker.make(
        projects_models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    )

    with login(client, user=membership.member):
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
    with login(client, groups=["switchtender"]):
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


def test_user_can_access_methodology(client):
    url = reverse("methodology")
    response = client.get(url)
    assert response.status_code == 200


def test_user_can_access_whoweare(client):
    url = reverse("whoweare")
    response = client.get(url)
    assert response.status_code == 200


def test_user_can_access_followus(client):
    url = reverse("followus")
    response = client.get(url)
    assert response.status_code == 200


# eof
