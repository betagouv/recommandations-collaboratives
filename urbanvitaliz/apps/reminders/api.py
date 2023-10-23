# encoding: utf-8

"""
Models for reminders

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 12:59:08 CEST
"""

import datetime

from django.utils import timezone

from . import models

from urbanvitaliz.apps.tasks.models import Task


def make_or_update_reminder(site, project, kind, deadline):
    if deadline < timezone.localdate():
        return None

    if site not in project.sites.all():
        return None

    existing_reminder = models.Reminder.on_site_to_send.filter(project=project).first()

    if existing_reminder:  # we have a reminder, update deadline
        existing_reminder.deadline = deadline
        existing_reminder.save()
        return existing_reminder

    else:  # create a new reminder for the deadline
        return models.Reminder.objects.create(
            site=site,
            project=project,
            deadline=deadline,
            kind=kind,
            origin=models.Reminder.SYSTEM,
        )

    return None


def make_or_update_new_recommendations_reminder(site, project):
    """Given a project, generate reminders for new recommendations that may have been
    missed by the council
    """
    last_task = (
        project.tasks.exclude(status__in=[Task.DONE, Task.NOT_INTERESTED])
        .exclude(public=False)
        .order_by("-created_on")
        .first()
    )

    if not last_task:
        return None

    # FIXME(glibersat) Should not be hardcoded
    interval = datetime.timedelta(days=10)  # in days

    deadline = last_task.created_on + interval

    return make_or_update_reminder(site, project, models.Reminder.NEW_RECO, deadline)


def make_whatups_reminders():
    ...


# eof
