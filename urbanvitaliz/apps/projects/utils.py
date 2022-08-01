# encoding: utf-8

"""
Utilities for projects

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: <2021-09-13 lun. 15:38>

"""

import uuid

from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.urls import reverse
from urbanvitaliz import utils as uv_utils
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
    Check if user is allowed to administrate the given project.
    If project is None, check if this user can at least administer one
    Administrators are mostly switchtenders/advisors
    """
    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    if project:
        return project.switchtenders_on_site.filter(switchtender=user).exists()
    else:
        return models.Project.on_site.filter(switchtenders=user).count() > 0


def can_administrate_or_403(project, user):
    """Raise a 403 error is user is not an assigned switchtender or admin"""
    if can_administrate_project(project, user):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def is_member(user, project, allow_draft):
    """return true if user is member of the project"""
    return (user in project.members.all()) and (
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


def get_national_actors():
    """Return national actors"""
    users = auth_models.User.objects.filter(groups__name="switchtender")
    users = users.filter(profile__departments=None)
    return users.distinct()


def is_regional_actor_for_project(project, user, allow_national=False):
    """Check if this user is a regional actor for a given project"""
    return user in get_regional_actors_for_project(project, allow_national)


def check_if_national_actor(user):
    """Check if this user is a national actor"""
    return user in get_national_actors()


def is_regional_actor_for_project_or_403(project, user, allow_national=False):
    if is_regional_actor_for_project(project, user, allow_national):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_switchtenders_for_project(project):
    """Return all the switchtenders for a given project"""
    return auth_models.User.objects.filter(
        projects_switchtended_on_site__project=project,
        projects_switchtended_on_site__site=get_current_site(request=None),
    ).distinct()


def get_collaborators_for_project(project):
    return project.members.all().distinct()


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
            project = models.Project.on_site.get(id=project_id)
        except models.Project.DoesNotExist:
            pass
    else:
        try:
            memberships = models.ProjectMember.objects.filter(
                Q(project__sites=get_current_site(request)),
                Q(project__deleted=None),
                Q(member=request.user),
                Q(is_owner=True) | Q(~Q(project__status="DRAFT"), is_owner=False),
            )

            if memberships.first():
                project = memberships.first().project

        except models.Project.DoesNotExist:
            pass

    return project


def set_active_project_id(request, project_id: int):
    """Set the current project in a session cookie"""
    request.session["active_project"] = project_id


def refresh_user_projects_in_session(request, user):
    """store the user projects in the session"""

    memberships = models.ProjectMember.objects.filter(
        Q(project__sites=get_current_site(request)),
        Q(project__deleted=None),
        Q(member=user),
        Q(is_owner=True) | Q(~Q(project__status="DRAFT"), is_owner=False),
    )

    projects = [m.project for m in memberships.all()]

    # projects = models.Project.objects.filter(deleted=None).filter(
    #    Q(members=user) | Q(~Q(status="DRAFT"), members=user)
    # )

    request.session["projects"] = list(
        {
            "name": p.name,
            "id": p.id,
            "location": p.location,
            "actions_open": p.tasks.open().count(),
        }
        for p in projects
    )


def make_rsvp_link(rsvp, status):
    return uv_utils.build_absolute_url(
        reverse("projects-rsvp-followup-task", args=(rsvp.pk, status))
    )


def create_reminder(days, task, user, origin):
    """
    Create a reminder using the reminder API and schedule a RSVP to send to the target user
    """
    if user.is_anonymous:
        return

    api.create_reminder_email(
        user.email,
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


def format_switchtender_identity(user):
    fmt = f"{user.first_name}"
    fmt += f" {user.last_name}"
    if user.profile and user.profile.organization:
        fmt += f" - {user.profile.organization.name}"

    return fmt
