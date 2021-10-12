# encoding: utf-8

"""
Models for reminders

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 12:59:08 CEST
"""

import datetime

from django.template import loader

from django.contrib.contenttypes.models import ContentType

from django.contrib.sites.shortcuts import get_current_site

from . import models


def create_reminder_email(
    request,
    recipient,
    subject,
    template_base_name,
    related,
    origin=0,
    delay=15,
    extra_context=None,
):
    """Prepare an email raw or html to be sent in delay days, inspired by magicauth"""

    # remove existing reminders for this recipient / related
    # NOTE should we only delete objects farther than the new deadline ?
    # NOTE discuss about only removing reminders from the same origin
    if not related:
        return
    content_type = ContentType.objects.get_for_model(related)
    models.Mail.to_send.filter(
        content_type=content_type, object_id=related.id, recipient=recipient
    ).delete()

    html_template = template_base_name + ".html"
    text_template = template_base_name + ".txt"

    context = {"site": get_current_site(request), "request": request}
    if extra_context:
        context.update(extra_context)

    text_message = loader.render_to_string(text_template, context)
    html_message = loader.render_to_string(html_template, context)

    deadline = datetime.date.today() + datetime.timedelta(days=delay)

    models.Mail(
        recipient=recipient,
        subject=subject,
        text=text_message,
        html=html_message,
        deadline=deadline,
        related=related,
        origin=origin,
    ).save()


def remove_reminder_email(related, recipient=None, origin=0):
    """Remove reminder if one exist for this object [w/ given recipient, origin]"""
    if not related:
        return
    content_type = ContentType.objects.get_for_model(related)
    reminders = models.Mail.to_send.filter(
        content_type=content_type,
        object_id=related.id,
    )
    if recipient:
        reminders = reminders.filter(recipient=recipient)
    if origin:
        reminders = reminders.filter(origin=origin)
    reminders.delete()


# eof
