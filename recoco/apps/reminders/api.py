# encoding: utf-8

"""
Models for reminders

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-09-28 12:59:08 CEST
"""

import datetime
import logging

from django.utils import timezone
from recoco.apps.tasks.models import Task
from recoco.apps.home.models import SiteConfiguration


from . import models

logger = logging.getLogger("main")


def make_or_update_reminder(site, project, kind, deadline):
    if site not in project.sites.all():
        return None

    existing_reminder = (
        models.Reminder.on_site_to_send.filter(project=project, kind=kind)
        .order_by("-deadline")
        .first()
    )

    task_count = (
        project.tasks.filter(status__in=Task.OPEN_STATUSES)
        .filter(site=site)
        .exclude(public=False)
        .count()
    )

    if (existing_reminder is None) and task_count == 0:
        return None

    if deadline < timezone.localdate():
        if existing_reminder:
            existing_reminder.delete()
            logger.warning(
                f"Deleting reminder {kind} since it is too old "
                f"for project <{project.name}>"
                f" ({project.pk})"
            )

        return None

    if existing_reminder:
        # check if this reminder still makes sense ; i.e. we still have unattended
        # Recommendations to remind. Delete it otherwise
        if task_count == 0:
            logger.warning(
                f"Deleting bogus {kind} reminder since there are no more"
                f"open tasks for project <{project.name}>"
                f" ({project.pk})"
            )
            existing_reminder.delete()
            return None
        else:
            if existing_reminder.deadline != deadline:
                existing_reminder.deadline = deadline
                existing_reminder.save()
                logger.info(
                    f"Updating reminder <{existing_reminder.kind}> "
                    f"for project <{project.name}>(id={project.pk})"
                )
            return existing_reminder

    logger.info(
        f"Creating reminder <{kind}> for project <{project.name}> "
        f"({project.pk}) ; deadline={deadline}"
    )
    return models.Reminder.objects.create(
        site=site,
        project=project,
        deadline=deadline,
        kind=kind,
        origin=models.Reminder.SYSTEM,
    )


def get_due_reminder_for_project(site, project, kind):
    """Return the current reminder (=not sent yet) for a given kind."""
    try:
        reminder = models.Reminder.on_site_to_send.get(
            project=project,
            site=site,
            kind=kind,
            deadline__lte=timezone.localdate(),  # today
        )
    except models.Reminder.DoesNotExist:
        return None

    if not reminder:
        logger.debug(f"No due <{kind}> reminder!")
        return None

    return reminder


#################################################################
# New Recommendations Reminder
#################################################################
def make_or_update_new_recommendations_reminder(site, project, interval_in_days=7 * 6):
    """Given a project, generate reminders for new recommendations that may have been
    missed by the council. Default interval is 6 weeks.
    """
    last_task = (
        project.tasks.filter(status__in=Task.OPEN_STATUSES)
        .filter(site=site)
        .exclude(public=False)
        .order_by("-created_on")
        .first()
    )

    last_sent_reminder = (
        models.Reminder.on_site_sent.filter(
            kind=models.Reminder.NEW_RECO, project=project
        )
        .order_by("-sent_on")
        .first()
    )

    if last_task:
        starting_point = last_task.created_on
    else:
        starting_point = timezone.now()

    if last_sent_reminder:
        if last_sent_reminder.sent_on > starting_point:
            starting_point = last_sent_reminder.sent_on

    interval = datetime.timedelta(days=interval_in_days)
    deadline = (starting_point + interval).date()

    return make_or_update_reminder(
        site=site, project=project, kind=models.Reminder.NEW_RECO, deadline=deadline
    )


def get_due_new_recommendations_reminder_for_project(site, project):
    return get_due_reminder_for_project(site, project, kind=models.Reminder.NEW_RECO)


#################################################################
# What's up? Reminder
#################################################################


def make_or_update_whatsup_reminder(site, project):
    """Given a project, generate a whats up email to the project owner to try to get her
    attention back. Interval is configured by the SiteConfiguration model.
    """
    last_activity = project.last_members_activity_at

    if not last_activity:
        logger.warning(
            f"Bogus project <{project.name}>(id={project.id}), "
            "no last members activity, using now()"
        )
        last_activity = timezone.now()

    starting_point = last_activity

    last_sent_reminder = (
        models.Reminder.on_site_sent.filter(
            project=project, kind=models.Reminder.WHATS_UP
        )
        .order_by("-sent_on")
        .first()
    )

    if last_sent_reminder:
        if last_sent_reminder.sent_on > starting_point:
            starting_point = last_sent_reminder.sent_on

    # Get our reminder interval by the current site configuration
    try:
        conf = site.configuration
        interval = datetime.timedelta(days=conf.reminder_interval)
    except SiteConfiguration.DoesNotExist:
        interval = datetime.timedelta(days=6 * 7)

    deadline = (starting_point + interval).date()

    if deadline < timezone.localdate():
        deadline = timezone.localdate()

    return make_or_update_reminder(
        site=site, project=project, kind=models.Reminder.WHATS_UP, deadline=deadline
    )


def get_due_whatsup_reminder_for_project(site, project):
    return get_due_reminder_for_project(site, project, kind=models.Reminder.WHATS_UP)


# eof
