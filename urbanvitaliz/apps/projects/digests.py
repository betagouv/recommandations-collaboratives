from itertools import groupby

from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from urbanvitaliz import utils
from urbanvitaliz.apps.communication.api import send_email

from . import models


def send_digests_for_new_recommendations_by_user(user):
    """
    For a given user, send a digest email containing all new recommendation.
    Each project generates a single email.
    """
    project_ct = ContentType.objects.get_for_model(models.Project)

    notifications = (
        user.notifications.unsent()
        .filter(target_content_type=project_ct, verb="a recommandé l'action")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return False

    skipped_projects = []
    for project_id, project_notifications in groupby(
        notifications, key=lambda x: x.target_object_id
    ):
        # Only treat notifications for project in DONE status
        project = models.Project.objects.get(pk=project_id)
        if project.status != "DONE":
            skipped_projects.append(project_id)
            continue

        recommendations = []
        notification_count = 0
        for notification in project_notifications:
            action = notification.action_object
            notification_count += 1

            action_link = utils.build_absolute_url(
                reverse("projects-project-detail", args=[action.project_id])
                + "#actions",
            )

            recommendations.append(
                {
                    "created_by": {
                        "first_name": action.created_by.first_name,
                        "last_name": action.created_by.last_name,
                    },
                    "intent": action.intent,
                    "url": action_link,
                }
            )

        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[action.project_id])
        )
        email_params = {
            "notification-count": notification_count,
            "project": {
                "name": action.project.name,
                "url": project_link,
                "commune": {
                    "postal": action.project.commune
                    and action.project.commune.postal
                    or "",
                    "name": action.project.commune
                    and action.project.commune.name
                    or "",
                },
            },
            "reco": recommendations,
        }

        send_email("new_recommendations_digest", user.email, params=email_params)

    # Mark them as dispatched
    notifications.exclude(target_object_id__in=skipped_projects).mark_as_sent()

    return True


def send_digests_for_new_sites_by_user(user):
    project_ct = ContentType.objects.get_for_model(models.Project)

    notifications = (
        user.notifications.unsent()
        .filter(target_content_type=project_ct, verb="a déposé le projet")
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return False

    for notification in notifications:
        project = notification.action_object
        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[project.pk])
        )
        email_params = {
            "project": {
                "name": project.name,
                "url": project_link,
                "commune": {
                    "postal": project.commune.postal,
                    "name": project.commune.name,
                },
            },
        }

        send_email("new_site_for_switchtender", user.email, params=email_params)

    # Mark them as dispatched
    notifications.mark_as_sent()

    return True


def send_digests_for_new_switchtenders_on_project_by_user(user):
    """
    When new switchtenders have joined a project, warn other regional
    switchtenders.
    """
    project_ct = ContentType.objects.get_for_model(models.Project)

    notifications = (
        user.notifications.unsent()
        .filter(
            target_content_type=project_ct,
            verb="est devenu·e aiguilleur·se sur le projet",
        )
        .order_by("target_object_id")
    )

    if notifications.count() == 0:
        return False

    for notification in notifications:
        project = notification.action_object
        switchtender = notification.actor
        project_link = utils.build_absolute_url(
            reverse("projects-project-detail", args=[project.pk])
        )
        email_params = {
            "switchtender": {
                "first_name": switchtender.first_name,
                "last_name": switchtender.last_name,
            },
            "project": {
                "name": project.name,
                "url": project_link,
                "commune": {
                    "postal": project.commune.postal,
                    "name": project.commune.name,
                },
            },
        }

        if switchtender.profile.organization:
            email_params["organization"] = switchtender.profile.organization.name

        send_email("new_site_for_switchtender", user.email, params=email_params)

    # Mark them as dispatched
    notifications.mark_as_sent()

    return True
