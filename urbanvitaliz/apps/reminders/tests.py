# encoding: utf-8

"""
Tests for reminders application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 13:17:53 CEST
"""

import datetime
import pytest

from django.test.client import RequestFactory

# from model_bakery.recipe import Recipe

from . import api
from . import models


@pytest.mark.django_db
def test_create_mail_reminder_using_provided_information():
    url = "/project/action/0/"
    request = RequestFactory().get(url)
    recipient = "test@example.com"
    subject = "[UV] action reminder"
    template = "reminders/test"
    delay = 14
    extra = {"notes": "some notes."}

    api.create_reminder_email(
        request, recipient, subject, template, delay=delay, extra_context=extra
    )

    reminder = models.Mail.to_send.all()[0]

    assert reminder.recipient == recipient
    assert reminder.subject == subject
    assert extra["notes"] in reminder.text
    assert url in reminder.text

    assert reminder.deadline == datetime.date.today() + datetime.timedelta(days=delay)


# eof
