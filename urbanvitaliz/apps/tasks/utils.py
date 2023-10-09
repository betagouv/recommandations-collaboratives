# encoding: utf-8

"""
Utilities for projects

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: <2021-09-13 lun. 15:38>

"""


from django.urls import reverse
from urbanvitaliz import utils as uv_utils
from urbanvitaliz.apps.reminders import api


def make_rsvp_link(rsvp, status):
    return uv_utils.build_absolute_url(
        reverse("projects-rsvp-followup-task", args=(rsvp.pk, status))
    )


def create_reminder(days, task, user, origin):
    """Create a reminder and schedule a RSVP for user

    Reminder is created using reminer API
    RSVP is to be sent to the target user
    """
    if user.is_anonymous:
        return

    api.create_reminder_email(
        recipient=user.email,
        related=task,
        origin=origin,
        delay=days,
    )

    return True


def remove_reminder(task, user, origin=None):
    """
    Remove a reminder using the reminder API
    """
    if user.is_anonymous:
        return

    api.remove_reminder_email(related=task, recipient=user.email, origin=origin)

    return True


# eof
