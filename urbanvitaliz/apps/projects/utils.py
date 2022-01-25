# encoding: utf-8

"""
Utilities for projects

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: <2021-09-13 lun. 15:38>

"""

import uuid
from itertools import groupby

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.reminders import api

from . import models


def can_manage_project(project, user, allow_draft=False):
    """
    Check if user is allowed to manage this project.
    Managing means editing most things, except internal data.
    Project managers are mostly team members of the project.
    """
    if user.is_anonymous:
        return False

    if is_member(user, project, allow_draft):
        return True

    if can_administrate_project(project, user):
        return True

    return False


def can_administrate_project(project, user):
    """
    Check if user is allowed to administrate this project.
    Administrators are mostly assigned switchtenders
    """
    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    return user in project.switchtenders.all()


def can_administrate_or_403(project, user):
    """Raise a 403 error is user is not an assigned switchtender or admin"""
    if can_administrate_project(project, user):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def is_member(user, project, allow_draft):
    """return true if user is member of the project"""
    return ((user.email == project.email) or (user.email in project.emails)) and (
        (project.status != "DRAFT") or allow_draft
    )  # noqa: F841


def in_allowed_departments(user, project):
    """return true if project is in allowed departments for user"""
    allowed = user.profile.departments.values_list("code", flat=True)
    if not allowed:  # empty list means full access
        return True
    return project.commune and (project.commune.department_id in allowed)


def can_manage_or_403(project, user, allow_draft=False):
    """Raise a 403 error is user is not a owner or admin"""
    if can_manage_project(project, user, allow_draft=allow_draft):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_project_moderators():
    """Return all the moderators for projects"""
    return auth_models.User.objects.filter(groups__name="project_moderator").filter(
        groups__name="switchtender"
    )


def is_project_moderator(user):
    """Check if this user is allowed to moderate new projects"""
    return (user in get_project_moderators()) or user.is_superuser


def is_project_moderator_or_403(user):
    if is_project_moderator(user):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_regional_actors_for_project(project, allow_national=False):
    """Return regional actors for a given project"""
    if not project.commune or not project.commune.department:
        return auth_models.User.objects.none()

    users = auth_models.User.objects.filter(groups__name="switchtender")

    area_filter = Q(profile__departments=project.commune.department)
    if allow_national:
        area_filter = area_filter | Q(profile__departments=None)

    users = users.filter(area_filter)

    return users.distinct()


def is_regional_actor_for_project(project, user, allow_national=False):
    """Check if this user is a regional actor for a given project"""
    return user in get_regional_actors_for_project(project, allow_national)


def is_regional_actor_for_project_or_403(project, user, allow_national=False):
    if is_regional_actor_for_project(project, user, allow_national):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_switchtenders_for_project(project):
    """Return all the switchtenders for a given project"""
    return project.switchtenders.all().distinct()


def get_switchtenders_for_project_old(project):
    """Return all the switchtenders for a given project"""
    users = auth_models.User.objects.filter(groups__name="switchtender")

    if project.commune and project.commune.department:
        users = users.filter(
            Q(profile__departments=project.commune.department)
            | Q(profile__departments=None)
        )

    return users.distinct()


def get_collaborators_for_project(project):
    return auth_models.User.objects.filter(email__in=project.emails).distinct()


def get_notification_recipients_for_project(project):
    """Get all the people that should receive notifications for a given project"""
    return (
        get_switchtenders_for_project(project) | get_collaborators_for_project(project)
    ).distinct()


def generate_ro_key():
    """Generate the ReadOnly key for sharing"""
    return uuid.uuid4().hex


def get_active_project_id(request):
    """Return the active project ID for a given user"""
    return request.session.get("active_project", None)


def get_active_project(request):
    """Return the active project for a given user"""
    if not request.user.is_authenticated:
        return None

    project_id = get_active_project_id(request)
    project = None

    if project_id:
        try:
            project = models.Project.objects.get(id=project_id)
        except models.Project.DoesNotExist:
            pass
    else:
        try:
            project = (
                models.Project.objects.filter(deleted=None)
                .filter(
                    Q(email=request.user.email)
                    | Q(~Q(status="DRAFT"), emails__contains=request.user.email)
                )
                .first()
            )
        except models.Project.DoesNotExist:
            pass

    return project


def set_active_project_id(request, project_id: int):
    """Set the current project in a session cookie"""
    request.session["active_project"] = project_id


def refresh_user_projects_in_session(request, user):
    """store the user projects in the session"""
    projects = models.Project.objects.filter(deleted=None).filter(
        Q(email=user.email) | Q(~Q(status="DRAFT"), emails__contains=user.email)
    )

    request.session["projects"] = list(
        {
            "name": p.name,
            "id": p.id,
            "location": p.location,
            "actions_open": p.tasks.open().count(),
        }
        for p in projects
    )


def create_reminder(request, days, task, recipient, origin):
    """
    Create a reminder using the reminder API and schedule a RSVP to send to the target user
    """
    subject = f'[UrbanVitaliz] Où en êtes vous suite à nos recommandations pour le site "{task.project.name}"'
    template = "projects/notifications/task_remind_email"

    target_user = None
    try:
        target_user = auth_models.User.objects.get(email=recipient)
    except auth_models.User.DoesNotExist:
        return False

    rsvp, created = models.TaskFollowupRsvp.objects.get_or_create(
        task=task, user=target_user
    )
    if not created:
        rsvp.created_on = timezone.now()
        rsvp.save()

    api.create_reminder_email(
        request,
        recipient,
        subject,
        template,
        related=task,
        origin=origin,
        delay=days,
        extra_context={"task": task, "delay": days, "rsvp": rsvp},
    )

    return True
