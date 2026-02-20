import datetime

import django.dispatch
from actstream import action
from actstream.models import action_object_stream
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from notifications import models as notifications_models
from notifications.signals import notify

from recoco import verbs
from recoco.apps.survey import signals as survey_signals
from recoco.apps.training import utils as training_utils
from recoco.utils import is_staff_for_site

from . import models
from .utils import (
    get_project_moderators,
    get_regional_actors_for_project,
    notify_advisors_of_project,
    notify_members_of_project,
    reactivate_if_necessary,
)

########################################################################
# Projects
########################################################################


project_submitted = django.dispatch.Signal()
project_validated = django.dispatch.Signal()
project_rejected = django.dispatch.Signal()

# not using default signal but our own for easier processing
project_userprojectstatus_updated = django.dispatch.Signal()

project_switchtender_joined = django.dispatch.Signal()
project_observer_joined = django.dispatch.Signal()
project_switchtender_leaved = django.dispatch.Signal()

project_member_joined = django.dispatch.Signal()
project_owner_joined = django.dispatch.Signal()

document_uploaded = django.dispatch.Signal()


@receiver(project_submitted)
def log_project_submitted(sender, site, submitter, project, **kwargs):
    action.send(
        sender=submitter,
        verb=verbs.Project.SUBMITTED_BY,
        action_object=project,
        target=project,
    )


@receiver(project_submitted)
def notify_moderators_project_submitted(sender, site, submitter, project, **kwargs):
    recipients = get_project_moderators(site)

    # Notify project moderators
    notify.send(
        sender=submitter,
        recipient=recipients,
        verb=verbs.Project.SUBMITTED_BY,
        action_object=project,
        target=project,
    )


@receiver(project_validated)
def log_project_validated(sender, site, moderator, project, **kwargs):
    action.send(
        sender=moderator,
        verb=verbs.Project.VALIDATED_BY,
        action_object=project,
        target=project,
    )

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    # prevent crashing on misconfigured object
    if not project.owner:
        return

    # Notify regional actors of a new project
    notify.send(
        sender=project.owner,
        recipient=get_regional_actors_for_project(site, project),
        verb=verbs.Project.AVAILABLE,
        action_object=project,
        target=project,
    )


@receiver(project_rejected)
def log_project_rejected(sender, site, moderator, project, **kwargs):
    action.send(
        sender=moderator,
        verb=verbs.Project.REJECTED_BY,
        action_object=project,
        target=project,
    )


@receiver(project_rejected)
def unnotify_project_submitted_on_rejection(site, project, **kwargs):
    project_ct = ContentType.objects.get_for_model(project)
    notifications_models.Notification.objects.filter(
        action_object_content_type=project_ct.pk,
        action_object_object_id=project.pk,
        site=site,
        verb=verbs.Project.SUBMITTED_BY,
    ).update(emailed=True, unread=False)


@receiver(
    pre_delete,
    sender=models.Project,
    dispatch_uid="project_delete_notifications",
)
def delete_notifications_on_project_delete(sender, instance, **kwargs):
    project_ct = ContentType.objects.get_for_model(instance)
    notifications_models.Notification.objects.filter(
        target_content_type=project_ct.pk, target_object_id=instance.pk
    ).delete()


@receiver(project_switchtender_joined)
def log_project_switchtender_joined(sender, project, **kwargs):
    action.send(
        sender,
        verb=verbs.Project.BECAME_ADVISOR,
        action_object=project,
        target=project,
    )


@receiver(project_switchtender_joined)
def notify_project_switchtender_joined(sender, project, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    notification = {
        "sender": sender,
        "verb": verbs.Project.BECAME_ADVISOR,
        "action_object": project,
        "target": project,
    }

    notify_advisors_of_project(project, notification, exclude=sender)
    if not project.inactive_since:
        notify_members_of_project(project, notification)


@receiver(project_observer_joined)
def log_project_observer_joined(sender, project, **kwargs):
    action.send(
        sender,
        verb=verbs.Project.BECAME_OBSERVER,
        action_object=project,
        target=project,
    )


@receiver(project_observer_joined)
def notify_project_observer_joined(sender, project, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    notification = {
        "sender": sender,
        "verb": verbs.Project.BECAME_OBSERVER,
        "action_object": project,
        "target": project,
    }

    notify_advisors_of_project(project, notification, exclude=sender)
    if not project.inactive_since:
        notify_members_of_project(project, notification)


@receiver(project_switchtender_leaved)
def log_project_switchtender_leaved(sender, project, **kwargs):
    action.send(
        sender,
        verb=verbs.Project.LEFT_ADVISING,
        action_object=project,
        target=project,
    )


@receiver(project_switchtender_leaved)
def delete_joined_on_switchtender_leaved_if_same_day(sender, project, **kwargs):
    project_ct = ContentType.objects.get_for_model(project)
    notifications_models.Notification.objects.filter(
        target_content_type=project_ct.pk,
        target_object_id=project.pk,
        verb=verbs.Project.BECAME_ADVISOR,
        timestamp__gte=timezone.now() - datetime.timedelta(hours=12),
    ).delete()


########################################################################
# Project Members
########################################################################


@receiver(project_member_joined)
def log_project_member_joined(sender, project, **kwargs):
    action.send(
        sender,
        verb=verbs.Project.JOINED,
        action_object=project,
        target=project,
    )


@receiver(project_owner_joined)
def log_project_owner_joined(sender, project, **kwargs):
    action.send(
        sender,
        verb=verbs.Project.JOINED_OWNER,
        action_object=project,
        target=project,
    )


@receiver(project_member_joined)
def notify_project_member_joined(sender, project, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    notification = {
        "sender": sender,
        "verb": verbs.Project.JOINED,
        "action_object": project,
        "target": project,
    }

    notify_advisors_of_project(project, notification)
    if not project.inactive_since:
        notify_members_of_project(project, notification, exclude=sender)


########################################################################
# Reminders
########################################################################

reminder_created = django.dispatch.Signal()


@receiver(reminder_created)
def log_reminder_created(sender, task, project, user, **kwargs):
    if not is_staff_for_site(user):
        action.send(
            user,
            verb=verbs.Recommendation.REMINDER_ADDED,
            action_object=task,
            target=project,
        )


######
# Notes
#####
note_created = django.dispatch.Signal()


# In case of deletion
@receiver(pre_delete, sender=models.Note, dispatch_uid="note_hard_delete_logs")
@receiver(pre_save, sender=models.Note, dispatch_uid="note_soft_delete_logs")
def delete_activity_on_note_delete(sender, instance, **kwargs):
    if instance.deleted is None:
        return

    project_ct = ContentType.objects.get_for_model(instance)
    notifications_models.Notification.objects.filter(
        target_content_type=project_ct.pk, target_object_id=instance.pk
    ).delete()

    action_object_stream(instance).delete()


@receiver(note_created)
def notify_note_created(sender, note, project, user, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    if note.public is False:
        action.send(
            user,
            verb=verbs.Conversation.PRIVATE_MESSAGE,
            action_object=note,
            target=project,
        )

        notification = {
            "sender": user,
            "verb": verbs.Conversation.PRIVATE_MESSAGE,
            "action_object": note,
            "target": project,
        }

        notify_advisors_of_project(project, notification, exclude=user)
    else:
        action.send(
            user,
            verb=verbs.Conversation.PUBLIC_MESSAGE,
            action_object=note,
            target=project,
        )

        notification = {
            "sender": user,
            "verb": verbs.Conversation.PUBLIC_MESSAGE,
            "action_object": note,
            "target": project,
        }

        notify_advisors_of_project(project, notification, exclude=user)
        if not project.inactive_since:
            notify_members_of_project(project, notification, exclude=user)


@receiver(note_created)
def note_created_challenged(sender, note, project, user, **kwargs):
    challenge = training_utils.get_challenge_for(user, "project-conversation-writer")
    if challenge and not challenge.acquired_on:
        challenge.acquired_on = timezone.now()
        challenge.save()


################################################################
# UserProjectStatus
################################################################


@receiver(project_userprojectstatus_updated)
def project_userproject_trace_status_changes(sender, old_one, new_one, **kwargs):
    if old_one and new_one:
        if old_one.status != new_one.status:
            action.send(
                new_one.user,
                verb=verbs.Project.USER_STATUS_UPDATED,
                action_object=new_one,
                target=new_one.project,
            )


################################################################
# File Upload
################################################################


@receiver(document_uploaded)
def project_document_uploaded(sender, instance, **kwargs):
    project = instance.project

    reactivate_if_necessary(project, instance.uploaded_by)

    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    # Add a trace
    action.send(
        instance.uploaded_by,
        verb=verbs.Document.ADDED,
        action_object=instance,
        target=project,
    )


################################################################
# Project Survey events
################################################################


@receiver(
    survey_signals.survey_session_updated,
    dispatch_uid="survey_answer_created_or_updated",
)
def log_survey_session_updated(sender, session, request, **kwargs):
    project = session.project
    user = request.user

    # If we already sent this notification less a day ago, skip it
    one_day_ago = timezone.now() - datetime.timedelta(days=1)
    if session.action_object_actions.filter(
        verb=verbs.Survey.UPDATED, timestamp__gte=one_day_ago
    ).count():
        return

    action.send(
        user,
        verb=verbs.Survey.UPDATED,
        action_object=session,
        target=session.project,
    )

    notification = {
        "sender": user,
        "verb": verbs.Survey.UPDATED,
        "action_object": session,
        "target": project,
    }

    notify_advisors_of_project(project, notification, exclude=user)


# eof
