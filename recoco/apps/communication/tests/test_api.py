# encoding: utf-8

"""
tests for digesting emails

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2022-02-03 16:14:54 CET
"""

import test  # noqa

import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.test import override_settings
from model_bakery import baker
from model_bakery.recipe import Recipe
from recoco.apps.home import models as home_models
from recoco.apps.projects import models as projects_models

from .. import api, brevo, models
from ..api import send_email


@pytest.mark.django_db
def test_send_email_call_send_debug_email_in_debug_mode(mocker, settings, request):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    django_send_mail_mock = mocker.patch(
        "recoco.apps.communication.api.django_send_mail"
    )
    brevo_mock = mocker.patch("recoco.apps.communication.brevo.Brevo.send_email")

    template_name = "a template"

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    api.send_email(template_name, user1.email, params={})

    brevo_mock.assert_not_called()
    django_send_mail_mock.assert_called_once()


@pytest.mark.django_db
def test_send_debug_email_creates_transaction_without_related(request):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    template_name = "a template"

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    api.send_debug_email(template_name, user1.email, params=None, test=True)

    assert models.TransactionRecord.objects.count() == 1

    transaction = models.TransactionRecord.objects.first()

    assert transaction.site == current_site
    assert transaction.sent_on is not None
    assert transaction.transaction_id is not None
    assert transaction.user == user1
    assert transaction.related is None


@pytest.mark.django_db
def test_send_debug_email_creates_transaction_with_multiple_recipients(request):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    template_name = "a template"

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user2 = Recipe(
        auth.User, username="Alice", first_name="Alice", last_name="Joe"
    ).make()

    user1.profile.sites.add(current_site)
    user2.profile.sites.add(current_site)

    recipients = [user1.email, user2.email]

    api.send_debug_email(
        template_name, recipients, params=None, test=True, related=None
    )

    assert models.TransactionRecord.objects.count() == 2


@pytest.mark.django_db
def test_send_debug_email_creates_transaction_with_related(request):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    template_name = "a template"

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    note = Recipe(projects_models.Note).make()

    user1.profile.sites.add(current_site)

    recipients = [user1.email]

    api.send_debug_email(
        template_name, recipients, params=None, test=True, related=note
    )

    assert models.TransactionRecord.objects.count() == 1

    transaction = models.TransactionRecord.objects.first()

    assert transaction.related == note


@pytest.mark.django_db
def test_send_brevo_email_creates_transaction(mocker, request):
    class TransacResponse:
        message_id = "this-is-an-id"

    mocker.patch(
        "sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email",
        return_value=TransacResponse(),
    )
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    template = baker.make(models.EmailTemplate, name="a template", site=current_site)

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    recipients = [{"name": user1.username, "email": user1.email}]

    api.brevo_email(template.name, recipients, params={})

    assert models.TransactionRecord.objects.count() == 1

    transaction = models.TransactionRecord.objects.first()
    assert transaction.faked is False
    assert transaction.transaction_id == TransacResponse.message_id


@pytest.mark.django_db
def test_send_brevo_email_non_existent_template(mocker, request):
    class TransacResponse:
        message_id = "this-is-an-id"

    mocker.patch(
        "recoco.apps.communication.brevo.Brevo.send_email",
        return_value=TransacResponse(),
    )

    template_name = "a non existent template"

    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    recipients = [{"name": user1.username, "email": user1.email}]

    result = api.brevo_email(template_name, recipients, params={})

    brevo.Brevo.send_email.assert_not_called()
    assert result is False


@pytest.mark.django_db
def test_send_brevo_email_use_default_template(mocker, request):
    class TransacResponse:
        message_id = "this-is-an-id"

    mocker.patch(
        "recoco.apps.communication.brevo.Brevo.send_email",
        return_value=TransacResponse(),
    )

    template_name = "a template"

    current_site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        legal_address="here",
        legal_owner="Doe",
        description="The short description",
        sender_email="doe@example.org",
    )

    template = baker.make(models.EmailTemplate, name=template_name, site=None)

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    recipients = [{"name": user1.username, "email": user1.email}]

    api.brevo_email(template_name, recipients, params={})

    brevo.Brevo.send_email.assert_called_once_with(
        template.sib_id,
        recipients,
        {
            "site_name": current_site.name,
            "site_domain": current_site.domain,
            "legal_address": "here",
            "legal_owner": "Doe",
            "description": "The short description",
            "sender_email": "doe@example.org",
        },
        test=False,
    )


@pytest.mark.django_db
def test_send_brevo_email_use_overrided_template(mocker, request):
    class TransacResponse:
        message_id = "this-is-an-id"

    mocker.patch(
        "recoco.apps.communication.brevo.Brevo.send_email",
        return_value=TransacResponse(),
    )

    template_name = "a template"

    current_site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        legal_address="here",
        legal_owner="Doe",
        description="The short description",
        sender_email="doe@example.org",
    )

    baker.make(models.EmailTemplate, name=template_name, site=None)
    overrided_template = baker.make(
        models.EmailTemplate, name=template_name, site=current_site
    )

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    recipients = [{"name": user1.username, "email": user1.email}]

    api.brevo_email(template_name, recipients, params={})

    brevo.Brevo.send_email.assert_called_once_with(
        overrided_template.sib_id,
        recipients,
        {
            "site_name": current_site.name,
            "site_domain": current_site.domain,
            "legal_address": "here",
            "legal_owner": "Doe",
            "description": "The short description",
            "sender_email": "doe@example.org",
        },
        test=False,
    )


@override_settings(
    BREVO_FORCE_DEBUG=True, DEBUG=True, DEBUG_EMAIL_WHITELIST=["superadmin@recoco.fr"]
)
def test_use_debug_filter(mocker):
    brevo_mock = mocker.patch("recoco.apps.communication.api.brevo_email")
    debug_mock = mocker.patch("recoco.apps.communication.api.send_debug_email")
    args = ("a template",)
    kwargs = {
        "params": "params",
        "test": "test",
        "related": "related",
    }
    white_listed_recipient = {"name": "admin", "email": "superadmin@recoco.fr"}
    random_recipient = "randomuser@recoco.fr"
    send_email(*args, [white_listed_recipient, random_recipient], **kwargs)
    # the assertion depends on giving args as args or kwargs, and it shouldn't need to be
    brevo_mock.assert_called_with(*args, [white_listed_recipient], **kwargs)
    debug_mock.assert_called_with(
        *args,
        [random_recipient],
        **kwargs,
    )
    pass
