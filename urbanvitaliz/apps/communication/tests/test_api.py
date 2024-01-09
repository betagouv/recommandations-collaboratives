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
from model_bakery import baker
from model_bakery.recipe import Recipe
from urbanvitaliz.apps.projects import models as projects_models

from .. import api, models


@pytest.mark.django_db
def test_send_debug_email_creates_transaction_without_related(request):
    current_site = get_current_site(request)

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
        messageId = 2

    mocker.patch(
        "sib_api_v3_sdk.TransactionalEmailsApi.send_transac_email",
        return_value=TransacResponse(),
    )
    current_site = get_current_site(request)

    template = baker.make(models.EmailTemplate, name="a template", site=current_site)

    user1 = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    user1.profile.sites.add(current_site)

    recipients = [{"name": user1.username, "email": user1.email}]

    api.brevo_email(template.name, recipients, params=None)

    assert models.TransactionRecord.objects.count() == 1

    transaction = models.TransactionRecord.objects.first()
    assert transaction.faked is False
    assert transaction.transaction_id == "2"
