# encoding: utf-8

"""
sending digest email to users and switchtenders

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
updated: 2022-02-03 16:16:37 CET
"""

from dataclasses import asdict, dataclass
from itertools import groupby

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.urls import reverse

from urbanvitaliz import utils, verbs
from urbanvitaliz.apps.tasks import models as tasks_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.reminders.api import (
    make_or_update_new_recommendations_reminder,
    make_or_update_whatsup_reminder,
    get_due_new_recommendations_reminder_for_project,
    get_due_whatsup_reminder_for_project,
)

from .api import send_email

import logging

logger = logging.getLogger("main")

########################################################################
# Reminders
########################################################################


def send_reminder_digests_by_project(project, dry_run=False):
    """
    Send a digest emails per project for each expired reminders
    """
    current_site = Site.objects.get_current()

    if not project.owner:
        logger.warning(
            f"No owner for project <{project.name}>(id={project.id}), "
            "skipping project reminders"
        )
        return False

    if project.inactive_since or project.muted:
        logger.info(
            f"Skipping inactive/muted project <{project.name}>(id={project.id})"
        )
        return False

    send_new_recommendations_reminders_digest_by_project(
        site=current_site, project=project, dry_run=dry_run
    )

    send_whatsup_reminders_digest_by_project(
        site=current_site, project=project, dry_run=dry_run
    )

    # Reschedule next reminders
    make_or_update_new_recommendations_reminder(current_site, project)
    make_or_update_whatsup_reminder(current_site, project)


def send_new_recommendations_reminders_digest_by_project(site, project, dry_run):
    """Send 'New Recommendation' reminder for the given project"""
    # Refresh reminders first
    make_or_update_new_recommendations_reminder(site, project)

    # Actually, send reminders
    due_reminder = get_due_new_recommendations_reminder_for_project(site, project)

    if not due_reminder:
        logger.debug("No NEW_RECO due reminder for project <{project.name}>, skipping")
        return False

    if not dry_run:
        tasks = (
            project.tasks.filter(status__in=tasks_models.Task.OPEN_STATUSES)
            .filter(site=site)
            .exclude(public=False)
            .order_by("-created_on")
        )

        digest = make_digest_of_project_recommendations(project, tasks, project.owner)
        send_email(
            "project_reminders_new_reco_digest",
            {"name": normalize_user_name(project.owner), "email": project.owner.email},
            params=digest,
        )
        logger.info(f"Sent NEW_RECO reminder <{due_reminder}>")

        # Mark as dispatched
        due_reminder.mark_as_sent()
    else:
        logger.info(f"[DRY RUN] Would have sent NEW_RECO reminder <{due_reminder}>")

    return True


def send_whatsup_reminders_digest_by_project(site, project, dry_run):
    """Send 'What's up? reminder for the given project"""
    # Refresh reminders first
    make_or_update_whatsup_reminder(site, project)

    # Actually, send reminders
    due_reminder = get_due_whatsup_reminder_for_project(site, project)

    if not due_reminder:
        logger.debug("No WHATSUP due reminder for <{project.name}>, skipping")
        return False

    if not dry_run:
        tasks = (
            project.tasks.filter(status__in=tasks_models.Task.OPEN_STATUSES)
            .filter(site=site)
            .exclude(public=False)
            .order_by("-created_on")
        )

        digest = make_digest_of_project_recommendations(project, tasks, project.owner)
        send_email(
            "project_reminders_whats_up_digest",
            {"name": normalize_user_name(project.owner), "email": project.owner.email},
            params=digest,
        )

        logger.info(f"Sent WHATS_UP reminder <{due_reminder}>")

        # Mark as dispatched
        due_reminder.mark_as_sent()
    else:
        logger.info(f"[DRY RUN] Would have sent WHATS_UP reminder <{due_reminder}>")

    return True


def send_reminder_digest_by_project_task(user, reminders, dry_run):
    """Send an email per project/user containing its reminders."""

    skipped_reminders = []
    for project_id, project_reminders in groupby(
        reminders, key=lambda x: x.related.project_id
    ):
        try:
            project = projects_models.Project.objects.get(pk=project_id)
        except projects_models.Project.DoesNotExist:
            for reminder in project_reminders:
                logger.warning(f"[W] Skipping bogus reminder <{reminder}>")
                skipped_reminders.append(reminder.pk)
            continue

        digest = make_digest_of_project_recommendations(project, reminders, user)
        if digest:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would have sent {len(digest)} digests to {user}."
                )
            else:
                send_email(
                    "project_reminders_digest",
                    {"name": normalize_user_name(user), "email": user.email},
                    params=digest,
                )

    return skipped_reminders


########################################################################
# reco digests
########################################################################


def send_digests_for_new_recommendations_by_user(user, dry_run):
    """
    Send a digest email per project with all its new recommendations for given user.
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    notifications = (
        user.notifications(manager="on_site")
        .unsent()
        .filter(target_content_type=project_ct, verb=verbs.Recommendation.CREATED)
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return 0

    skipped_projects = send_recommendation_digest_by_project(
        user, notifications, dry_run
    )

    if not dry_run:
        # Mark them as dispatched
        notifications.exclude(target_object_id__in=skipped_projects).mark_as_sent()

    return notifications.exclude(target_object_id__in=skipped_projects).count()


def send_recommendation_digest_by_project(user, notifications, dry_run):
    """Send an email per project containing its notifications."""

    skipped_projects = []
    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        try:
            project = projects_models.Project.objects.get(pk=project_id)
        except projects_models.Project.DoesNotExist:
            # Probably a deleted project?
            continue

        digest = make_digest_of_project_recommendations_from_notifications(
            project, project_notifications, user
        )

        if not dry_run:
            send_email(
                "new_recommendations_digest",
                {"name": normalize_user_name(user), "email": user.email},
                params=digest,
            )
        else:
            logger.info(
                f"[DRY RUN] Would have sent {len(digest)} notifications for <{user}>."
            )

    return skipped_projects


def make_digest_of_project_recommendations_from_notifications(
    project, project_notifications, user
):
    """Return digest for project recommendations to be sent to user"""
    actions = [notification.action_object for notification in project_notifications]

    return make_digest_of_project_recommendations(project, actions, user)


def make_digest_of_project_recommendations(project, tasks, user):
    """Return digest for project recommendations to be sent to user"""
    recommendations = make_recommendations_digest(tasks, user)
    project_digest = make_project_digest(project, user, url_name="actions")
    return {
        "notification_count": len(recommendations),
        "project": project_digest,
        "recos": recommendations,
    }


def make_recommendations_digest(recommendations, user):
    """Return a digest of all project recommendations"""
    recommendation_digest = []

    for recommendation in recommendations:
        action_digest = make_action_digest(recommendation, user)
        recommendation_digest.append(action_digest)

    return recommendation_digest


def make_project_digest(project, user=None, url_name="overview"):
    """Return base information digest for project"""
    project_link = utils.build_absolute_url(
        reverse(f"projects-project-detail-{url_name}", args=[project.id]),
        auto_login_user=user,
    )
    return {
        "name": project.name,
        "url": project_link,
        "commune": {
            "postal": project.commune and project.commune.postal or "",
            "name": project.commune and project.commune.name or "",
        },
    }


def make_action_digest(action, user):
    """Return digest of action"""

    if not action:
        return

    action_link = utils.build_absolute_url(
        reverse("projects-project-detail-actions", args=[action.project_id])
        + f"#action-{action.id}",
        auto_login_user=user,
    )
    return {
        "created_by": {
            "first_name": action.created_by.first_name,
            "last_name": action.created_by.last_name,
            "organization": {
                "name": (
                    action.created_by.profile.organization
                    and action.created_by.profile.organization.name
                    or ""
                )
            },
        },
        "intent": action.intent,
        "content": action.content[:50],
        "resource": {
            "title": action.resource and action.resource.title or "",
        },
        "url": action_link,
    }


########################################################################
# new site digests
########################################################################


def send_digests_for_new_sites_by_user(user, dry_run=False):
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    notifications = (
        user.notifications(manager="on_site")
        .unsent()
        .filter(target_content_type=project_ct, verb=verbs.Project.AVAILABLE)
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return 0

    send_new_site_digest_by_user(user, notifications, dry_run=dry_run)

    if not dry_run:
        # Mark them as dispatched
        notifications.mark_as_sent()

    return notifications.count()


def send_new_site_digest_by_user(user, notifications, dry_run):
    """Send digest of new site by user"""

    for notification in notifications:
        digest = make_digest_for_new_site(notification, user)
        if digest:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would have sent {len(digest)} notifications for {user}."
                )
            else:
                send_email(
                    "new_site_for_switchtender",
                    {"name": normalize_user_name(user), "email": user.email},
                    params=digest,
                )


def make_digest_for_new_site(notification, user):
    """Return a digest of new site from notification"""
    project = notification.action_object
    if not project:
        return None

    project_link = utils.build_absolute_url(
        reverse("projects-project-detail", args=[project.pk]), auto_login_user=user
    )
    # NOTE mose information associated to project on this one.  can we make
    # the same for all ? so make_project_digest could be used in all
    # places?
    return {
        "dashboard_url": utils.build_absolute_url(
            reverse("projects-project-list"), auto_login_user=user
        ),
        "project": {
            "name": project.name,
            "org_name": project.org_name,
            "url": project_link,
            "commune": {
                "postal": project.commune.postal,
                "name": project.commune.name,
                "department": {
                    "code": project.commune.department.code,
                    "name": project.commune.department.name,
                },
            },
        },
    }


########################################################################
# send digest by user
########################################################################


def send_digest_for_non_switchtender_by_user(user, dry_run=False):
    """
    Digest containing generic notifications (=those which weren't collected)
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    queryset = (
        user.notifications(manager="on_site")
        .filter(target_content_type=project_ct)
        .exclude(target_content_type=project_ct, verb=verbs.Recommendation.CREATED)
        .unsent()
    )

    return send_digest_by_user(
        user, template_name="digest_for_non_switchtender", queryset=queryset
    )


def send_digest_for_switchtender_by_user(user, dry_run=False):
    """
    Digest containing generic notifications (=those which weren't collected)
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    queryset = (
        user.notifications(manager="on_site")
        .filter(target_content_type=project_ct)
        .exclude(verb=verbs.Recommendation.CREATED)
        .unsent()
    )

    context = {
        "dashboard_url": utils.build_absolute_url(
            reverse("projects-project-list"), auto_login_user=user
        )
    }

    return send_digest_by_user(
        user,
        template_name="digest_for_switchtender",
        queryset=queryset,
        extra_context=context,
        dry_run=dry_run,
    )


def send_digest_by_user(
    user, template_name, queryset=None, extra_context=None, dry_run=False
):
    """
    Should be run at the end, to collect remaining notifications
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    if not queryset:
        notifications = (
            user.notifications(manager="on_site")
            .filter(target_content_type=project_ct)
            .unsent()
        )
    else:
        notifications = queryset

    notifications.order_by("target_object_id")

    if notifications.count() == 0:
        return 0

    projects_digest = make_remaining_notifications_digest(notifications, user)
    notification_count = sum(
        [project["notification_count"] for project in projects_digest]
    )
    digest = {
        "projects": projects_digest,
        "notification_count": notification_count,
    }

    if extra_context:
        digest.update(extra_context)

    if notification_count > 0:
        if not dry_run:
            send_email(
                template_name,
                {"name": normalize_user_name(user), "email": user.email},
                params=digest,
            )
        else:
            logger.info(
                f"[DRY RUN] Would have sent {len(digest)} notifications to <{user}>."
            )

    if not dry_run:
        # Mark them as dispatched
        notifications.mark_as_sent()

    return notifications.count()


def make_remaining_notifications_digest(notifications, user):
    """Return digests for given notifications"""
    digest = []

    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        project_digest = make_project_notifications_digest(
            project_id, project_notifications, user
        )
        if project_digest:
            digest.append(project_digest)

    return digest


def make_project_notifications_digest(project_id, notifications, user):
    """Return digest for given project notification"""
    # Ignore deleted projects
    try:
        project = projects_models.Project.objects.get(pk=project_id)
    except projects_models.Project.DoesNotExist:
        return None

    digest = make_project_digest(project, user)

    notifications_digest = make_notifications_digest(notifications)
    digest.update(
        {
            "notifications": notifications_digest,
            "notification_count": len(notifications_digest),
        }
    )
    return digest


def make_notifications_digest(notifications):
    """Return digest of given notifications"""
    formatter = NotificationFormatter()
    return [
        asdict(formatter.format(notification))
        for notification in notifications
        if notification is not None
    ]


########################################################################
# helpers
########################################################################


def normalize_user_name(user):
    """Return a user full name or standard greeting by default"""
    user_name = f"{user.first_name} {user.last_name}"
    if user_name.strip() == "":
        user_name = "Madame/Monsieur"
    return user_name


@dataclass
class FormattedNotification:
    summary: str
    excerpt: str = None


class NotificationFormatter:
    def __init__(self):
        self.dispatch_table = {
            verbs.Conversation.PUBLIC_MESSAGE: self.format_public_note_created,
            verbs.Conversation.PRIVATE_MESSAGE: self.format_private_note_created,
            verbs.Project.BECAME_ADVISOR: self.format_action_became_advisor,
            verbs.Project.BECAME_OBSERVER: self.format_action_became_observer,
            verbs.Project.AVAILABLE: self.format_new_project_available,
            verbs.Project.SUBMITTED_BY: self.format_project_submitted,
            verbs.Recommendation.COMMENTED: self.format_action_commented,
            verbs.Recommendation.CREATED: self.format_action_recommended,
            verbs.Document.ADDED: self.format_document_uploaded,
        }

    def format(self, notification):
        """
        Try formatting the notification by the dispatch table or
        use the default reprensentation
        """

        def _default(notification):
            summary = "{n.actor} {n.verb} {n.action_object}".format(n=notification)
            return FormattedNotification(summary=summary)

        fmt = self.dispatch_table.get(notification.verb, _default)
        return fmt(notification)

    # ------ Formatter Utils -----#
    def _represent_user(self, user):
        if not user:
            fmt = "--compte indisponible--"
            return fmt

        if user.last_name:
            fmt = f"{user.first_name} {user.last_name}"
        else:
            fmt = f"{user}"

        if user.profile.organization:
            fmt += f" ({user.profile.organization.name})"

        return fmt

    def _represent_recommendation(self, recommendation):
        if recommendation.resource:
            return recommendation.resource.title

        return recommendation.intent

    def _represent_recommendation_excerpt(self, recommendation):
        return recommendation.content[:50]

    def _represent_project(self, project):
        fmt = f"{project.name}"
        if project.commune:
            fmt += f" ({project.commune})"

        return fmt

    def _represent_project_excerpt(self, project):
        if project.description:
            return project.description[:50]

        return None

    def _represent_note_excerpt(self, note):
        return note.content[:200] or None

    def _represent_followup(self, followup):
        return followup.comment[:50]

    # -------- Routers -----------#
    # ------ Real Formatters -----#
    def format_public_note_created(self, notification):
        """A public note was written by a user"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Conversation.PUBLIC_MESSAGE}"
        excerpt = self._represent_note_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_private_note_created(self, notification):
        """A note was written by a switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Conversation.PRIVATE_MESSAGE}"
        excerpt = self._represent_note_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_document_uploaded(self, notification):
        """A document was uploaded by a user"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Document.ADDED}"

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_recommended(self, notification):
        """An action was recommended by a switchtender"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_recommendation(notification.action_object)
        summary = f"{subject} {verbs.Recommendation.CREATED} '{complement}'"
        excerpt = self._represent_recommendation_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_commented(self, notification):
        """An action was commented by someone"""
        subject = self._represent_user(notification.actor)

        if notification.action_object is None:
            summary = f"{subject} {verbs.Recommendation.COMMENTED}"
            excerpt = ""
        else:
            complement = self._represent_recommendation(notification.action_object.task)
            summary = f"{subject} a commenté la recommandation '{complement}'"
            excerpt = self._represent_followup(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_became_switchtender(self, notification):
        """Someone joined a project as switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} s'est joint·e à l'équipe de conseil."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_became_advisor(self, notification):
        """Someone joined a project as advisor"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Project.BECAME_ADVISOR}."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_became_observer(self, notification):
        """Someone joined a project as observer"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Project.BECAME_OBSERVER}."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_project_submitted(self, notification):
        """A project was submitted for moderation"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} {verbs.Project.SUBMITTED_BY}: '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_new_project_available(self, notification):
        """A new project is now available"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} {verbs.Project.AVAILABLE} '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)


# eof
