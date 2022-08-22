# encoding: utf-8

"""
sending digest email to users and switchtenders

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
updated: 2022-02-03 16:16:37 CET
"""

from dataclasses import asdict, dataclass
from datetime import timedelta
from itertools import groupby

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.utils import timezone
from multimethod import multimethod
from urbanvitaliz import utils
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.reminders import models as reminders_models

from .api import send_email

########################################################################
# Reminders
########################################################################


def send_digests_for_task_reminders_by_user(user):
    """
    Send a digest email per project with expired reminders
    """
    task_ct = ContentType.objects.get_for_model(projects_models.Task)

    now = timezone.now()

    # Fetch all Task Reminders
    reminders = reminders_models.Reminder.to_send.filter(
        recipient=user.email, deadline__lte=now
    ).filter(content_type=task_ct)

    if reminders.count() == 0:
        return 0

    skipped_reminders = send_reminder_digest_by_project_task(user, reminders)

    # Rearm for the next alarm, in 6 weeks
    for reminder in reminders.exclude(object_id__in=skipped_reminders):
        reminders_models.Reminder.objects.create(
            recipient=reminder.recipient,
            deadline=now + timedelta(weeks=6),
            origin=reminders_models.Reminder.SYSTEM,
            content_type=reminder.content_type,
            object_id=reminder.object_id,
        )

    # Mark as dispatched
    reminders.exclude(object_id__in=skipped_reminders).update(sent_on=now)

    # Delete the bogus ones
    reminders.filter(object_id__in=skipped_reminders).delete()

    return reminders.exclude(object_id__in=skipped_reminders).count()


def send_reminder_digest_by_project_task(user, reminders):
    """Send an email per project/user containing its reminders."""

    skipped_reminders = []
    for project_id, project_reminders in groupby(
        reminders, key=lambda x: x.related.project_id
    ):
        try:
            project = projects_models.Project.objects.get(pk=project_id)
        except projects_models.Project.DoesNotExist:
            for reminder in project_reminders:
                print(f"[W] Skipping reminder {reminder}")
                skipped_reminders.append(reminder.pk)
            continue

        digest = make_digest_of_reminders(project, reminders, user)

        send_email(
            "project_reminders_digest",
            {"name": normalize_user_name(user), "email": user.email},
            params=digest,
        )

    return skipped_reminders


def make_digest_of_reminders(project, reminders, user):
    """Return digest for reminders of a project to be sent to user"""
    task_digest = make_reminders_task_digest(reminders, user)
    project_digest = make_project_digest(project, user)
    return {
        "notification_count": len(reminders),
        "project": project_digest,
        "recos": task_digest,
    }


def make_reminders_task_digest(reminders, user):
    """Return a digest of all reminders tasks"""
    tasks = []

    for reminder in reminders:
        recommendation = make_action_digest(reminder.related, user)
        tasks.append(recommendation)

    return tasks


########################################################################
# reco digests
########################################################################


def send_digests_for_new_recommendations_by_user(user):
    """
    Send a digest email per project with all its new recommendations for given user.
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    notifications = (
        user.notifications(manager="on_site")
        .unsent()
        .filter(target_content_type=project_ct, verb="a recommandé l'action")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return 0

    skipped_projects = send_recommendation_digest_by_project(user, notifications)

    # Mark them as dispatched
    # NOTE it would mean more db request but could be more lean in inner function
    notifications.exclude(target_object_id__in=skipped_projects).mark_as_sent()

    return notifications.exclude(target_object_id__in=skipped_projects).count()


def send_recommendation_digest_by_project(user, notifications):
    """Send an email per project containing its notifications."""

    skipped_projects = []
    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        try:
            project = projects_models.Project.on_site.get(pk=project_id)
        except projects_models.Project.DoesNotExist:
            # Probably a deleted project?
            continue

        digest = make_digest_of_project_recommendations(
            project, project_notifications, user
        )

        send_email(
            "new_recommendations_digest",
            {"name": normalize_user_name(user), "email": user.email},
            params=digest,
        )

    return skipped_projects


def make_digest_of_project_recommendations(project, project_notifications, user):
    """Return digest for project recommendations to be sent to user"""
    recommendations = make_recommendations_digest(project_notifications, user)
    project_digest = make_project_digest(project, user, url_name="actions")
    return {
        "notification_count": len(recommendations),
        "project": project_digest,
        "recos": recommendations,
    }


def make_recommendations_digest(project_notifications, user):
    """Return a digest of all project recommendations"""
    recommendations = []

    for notification in project_notifications:
        action = notification.action_object
        recommendation = make_action_digest(action, user)
        recommendations.append(recommendation)

    return recommendations


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


def send_digests_for_new_sites_by_user(user):
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    notifications = (
        user.notifications(manager="on_site")
        .unsent()
        .filter(target_content_type=project_ct, verb="a déposé le projet")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return 0

    send_new_site_digest_by_user(user, notifications)

    # Mark them as dispatched
    # NOTE it would mean more db request but could be more lean in inner function
    notifications.mark_as_sent()

    return notifications.count()


def send_new_site_digest_by_user(user, notifications):
    """Send digest of new site by user"""

    for notification in notifications:
        digest = make_digest_for_new_site(notification, user)
        if digest:
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


def send_digest_for_non_switchtender_by_user(user):
    """
    Digest containing generic notifications (=those which weren't collected)
    """
    project_ct = ContentType.objects.get_for_model(projects_models.Project)

    queryset = (
        user.notifications(manager="on_site")
        .exclude(target_content_type=project_ct, verb="a recommandé l'action")
        .unsent()
    )

    return send_digest_by_user(
        user, template_name="digest_for_non_switchtender", queryset=queryset
    )


def send_digest_for_switchtender_by_user(user):
    """
    Digest containing generic notifications (=those which weren't collected)
    """
    queryset = (
        user.notifications(manager="on_site")
        .exclude(verb="a recommandé l'action")
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
    )


def send_digest_by_user(user, template_name, queryset=None, extra_context=None):
    """
    Should be run at the end, to collect remaining notifications
    """
    if not queryset:
        notifications = user.notifications(manager="on_site").unsent()
    else:
        notifications = queryset

    notifications.order_by("target_object_id")

    if notifications.count() == 0:
        return 0

    projects_digest = make_remaining_notifications_digest(notifications, user)

    digest = {
        "projects": projects_digest,
        "notification_count": notifications.count(),
    }

    if extra_context:
        digest.update(extra_context)

    if len(digest) > 0:
        send_email(
            template_name,
            {"name": normalize_user_name(user), "email": user.email},
            params=digest,
        )

    # Mark them as dispatched
    # NOTE it would mean more db request but could be more lean in inner function
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
        project = projects_models.Project.on_site.get(pk=project_id)
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
    return [asdict(formatter.format(notification)) for notification in notifications]


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
    def format(self, notification):
        return self.format_for_actor(notification.actor, notification)

    def _format_or_default(self, dispatch_table, notification):
        """
        Try formatting the notification by the dispatch table or
        use the default reprensentation
        """
        try:
            return dispatch_table[notification.verb](notification)
        except KeyError:
            return FormattedNotification(
                summary=f"{notification.actor} {notification.verb} {notification.action_object}"
            )

    # ------ Formatter Utils -----#
    def _represent_user(self, user):
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
        return note.content[:50] or None

    def _represent_followup(self, followup):
        return followup.comment[:50]

    # -------- Routers -----------#
    @multimethod
    def format_for_actor(self, actor: auth_models.User, notification):
        """Format for User"""
        return self._format_or_default(
            {
                "a créé une note de suivi": self.format_note_created,
                "est devenu·e aiguilleur·se sur le projet": self.format_action_became_switchtender,
                "a déposé le projet": self.format_new_project_available,
                "a soumis pour modération le projet": self.format_project_submitted,
                "a commenté l'action": self.format_action_commented,
                "a recommandé l'action": self.format_action_recommended,
                "a ajouté un document": self.format_document_uploaded,
            },
            notification,
        )

    # ------ Real Formatters -----#
    def format_note_created(self, notification):
        """An action was recommended by a switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} a rédigé une note de suivi"
        excerpt = self._represent_note_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_document_uploaded(self, notification):
        """A document was uploaded by a user"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} a ajouté un document"

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_recommended(self, notification):
        """An action was recommended by a switchtender"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_recommendation(notification.action_object)
        summary = f"{subject} a recommandé '{complement}'"
        excerpt = self._represent_recommendation_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_commented(self, notification):
        """An action was commented by someone"""
        subject = self._represent_user(notification.actor)

        if notification.action_object is None:
            summary = f"{subject} a commenté une recommandation"
            excerpt = ""
        else:
            complement = self._represent_recommendation(notification.action_object.task)
            summary = f"{subject} a commenté la recommandation '{complement}'"
            excerpt = self._represent_followup(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_became_switchtender(self, notification):
        """Someone joined a project as switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} s'est joint·e à l'équipe d'aiguillage."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_project_submitted(self, notification):
        """A project was submitted for moderation"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} a soumis pour modération le projet '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_new_project_available(self, notification):
        """A new project is now available"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} a déposé le projet '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)


# eof
