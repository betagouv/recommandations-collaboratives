# encoding: utf-8

"""
Models for reminders

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 12:59:08 CEST
"""

import datetime

from django.contrib.contenttypes.models import ContentType
from urbanvitaliz.apps.communication import models as communication_models

from . import models


def create_reminder_email(
    recipient,
    related,
    origin=models.Reminder.SYSTEM,
    delay=15,
):
    """Prepare an email raw or html to be sent in delay days, inspired by magicauth"""

    # remove existing reminders for this recipient / related
    # NOTE should we only delete objects farther than the new deadline ?
    # NOTE discuss about only removing reminders from the same origin
    if not related:
        return
    content_type = ContentType.objects.get_for_model(related)

    # Remove old ones
    models.Reminder.to_send.filter(
        content_type=content_type, object_id=related.id, recipient=recipient
    ).delete()

    deadline = datetime.date.today() + datetime.timedelta(days=delay)

    models.Reminder(
        recipient=recipient,
        deadline=deadline,
        related=related,
        origin=origin,
    ).save()


def remove_reminder_email(related, recipient=None, origin=models.Reminder.SYSTEM):
    """Remove reminder if one exist for this object [w/ given recipient, origin]"""
    if not related:
        return
    content_type = ContentType.objects.get_for_model(related)
    reminders = models.Reminder.to_send.filter(
        content_type=content_type,
        object_id=related.id,
    )
    if recipient:
        reminders = reminders.filter(recipient=recipient)
    if origin:
        reminders = reminders.filter(origin=origin)
    reminders.delete()


# eof
