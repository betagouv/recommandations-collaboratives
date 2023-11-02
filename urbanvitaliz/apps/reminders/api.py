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

    existing_reminder = models.Reminder.on_site_to_send.filter(
        project=project, kind=kind
    ).first()

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


def get_due_reminder_for_project(site, project, kind):
    """Return the current reminder (=not sent yet) for a given kind"""
    try:
        return models.Reminder.on_site_to_send.get(
            project=project,
            site=site,
            kind=kind,
            deadline__lte=timezone.localdate(),  # today
        )
    except models.Reminder.DoesNotExist:
        return None


#################################################################
# New Recommendations Reminder
#################################################################


def make_or_update_new_recommendations_reminder(site, project):
    """Given a project, generate reminders for new recommendations that may have been
    missed by the council
    """
    last_task = (
        project.tasks.filter(status__in=Task.OPEN_STATUSES)
        .filter(site=site)
        .exclude(public=False)
        .order_by("-created_on")
        .first()
    )

    if not last_task:
        return None

    # FIXME(glibersat) Should not be hardcoded
    interval = datetime.timedelta(days=10)  # in days

    deadline = (last_task.created_on + interval).date()

    return make_or_update_reminder(
        site=site, project=project, kind=models.Reminder.NEW_RECO, deadline=deadline
    )


def get_due_new_recommendations_reminder_for_project(site, project):
    reminder = get_due_reminder_for_project(
        site, project, kind=models.Reminder.NEW_RECO
    )

    if not reminder:
        print("[W] No due reminder!")
        return None

    # check if this reminder still makes sense ; i.e. we still have unattended
    # Recommendations to remind. Delete it otherwise
    if not (
        project.tasks.filter(status__in=Task.OPEN_STATUSES)
        .filter(site=site)
        .exclude(public=False)
        .count()
    ):
        print(
            "[W] Deleting bogus reminder since no tasks are "
            "still active for project <{project.name}>"
            f" ({project.pk})\n"
        )
        reminder.delete()
        return None

    return reminder


#################################################################
# What's up? Reminder
#################################################################


def make_whatups_reminders():
    ...


# eof
