# encoding: utf-8

"""
Utilities for projects

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: <2021-09-13 lun. 15:38>

"""

import uuid
from typing import TYPE_CHECKING

from django.contrib.auth import models as auth_models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from guardian.shortcuts import assign_perm, get_users_with_perms, remove_perm
from notifications.signals import notify

from recoco import utils as uv_utils

from . import models

if TYPE_CHECKING:
    from .models import Project, ProjectSwitchtender


@transaction.atomic
def assign_collaborator_permissions(user, project):
    """
    Assign permissions to project collaborator.

    If the project is still in draft (not accepted by moderators)
    """
    permissions = models.COLLABORATOR_DRAFT_PERMISSIONS
    if project.project_sites.current().status != "DRAFT":
        permissions += models.COLLABORATOR_PERMISSIONS

    for perm in permissions:
        try:
            assign_perm(perm, user, project)
        except auth_models.Permission.DoesNotExist as e:
            print(f"Unable to find permission <{perm}>, aborting.")
            raise e


@transaction.atomic
def assign_collaborator(user, project, is_owner=False):
    """Make someone becomes a project collaborator and assign permissions"""

    assign_collaborator_permissions(user, project)

    # if we already have an owner, don't allow her to be replaced
    if is_owner:
        if (
            models.ProjectMember.objects.exclude(member=user)
            .filter(project=project, is_owner=True)
            .exists()
        ):
            is_owner = False

    _, created = models.ProjectMember.objects.get_or_create(
        project=project, member=user, defaults={"is_owner": is_owner}
    )

    return created


@transaction.atomic
def unassign_collaborator(user, project):
    """Remove someone from being a project collaborator"""
    permissions = (
        models.COLLABORATOR_DRAFT_PERMISSIONS + models.COLLABORATOR_PERMISSIONS
    )

    for perm in permissions:
        try:
            remove_perm(perm, user, project)
        except auth_models.Permission.DoesNotExist:
            pass

    models.ProjectMember.objects.filter(
        member=user,
        project=project,
    ).delete()


@transaction.atomic
def assign_advisor(user, project, site=None):
    """
    Make someone becomes a project advisor
    FIXME site is not honored by "assign_perm".
    """
    site = site or Site.objects.get_current()

    for perm in models.ADVISOR_PERMISSIONS:
        try:
            assign_perm(perm, user, project)
        except auth_models.Permission.DoesNotExist as e:
            print(f"Unable to find permission <{perm}>, aborting.")
            raise e

    switchtending, created = models.ProjectSwitchtender.objects.get_or_create(
        switchtender=user,
        site=site,
        project=project,
        defaults={"is_observer": False},  # FIXME is_observer=True requested by default
    )

    if not created:  # FIXME is_observer=True requested by default
        switchtending.is_observer = False
        switchtending.save()

    return created


@transaction.atomic
def unassign_advisor(user, project, site=None):
    """
    Remove someone from being a project advisor
    FIXME site is not honored by "assign_perm".
    """
    site = site or Site.objects.get_current()

    for perm in models.ADVISOR_PERMISSIONS:
        try:
            remove_perm(perm, user, project)
        except auth_models.Permission.DoesNotExist:
            pass

    models.ProjectSwitchtender.objects.filter(
        switchtender=user,
        site=site,
        project=project,
    ).delete()


@transaction.atomic
def assign_observer(user, project, site=None):
    """
    Make someone becomes a project observer
    FIXME site is not honored by "assign_perm".
    """
    site = site or Site.objects.get_current()

    for perm in models.OBSERVER_PERMISSIONS:
        try:
            assign_perm(perm, user, project)
        except auth_models.Permission.DoesNotExist as e:
            print(f"Unable to find permission <{perm}>, aborting.")
            raise e

    switchtending, created = models.ProjectSwitchtender.objects.get_or_create(
        switchtender=user,
        site=site,
        project=project,
        defaults={"is_observer": True},
    )

    if not created:
        switchtending.is_observer = True
        switchtending.save()

    return created


# XXX currently no difference, but may need different perms in the future
unassign_observer = unassign_advisor


def can_administrate_project(project, user):
    """
    Check if user is allowed to administrate the given project on current site.
    If project is None, check if this user can at least administer one on site.
    Administrators are mostly switchtenders/advisors
    """
    if user.is_anonymous:
        return False

    if user.is_superuser:
        return True

    # FIXME replace by checking permissions
    if project:
        return project.switchtender_sites.on_site().filter(switchtender=user).exists()
    else:
        return models.Project.on_site.filter(switchtenders=user).exists()


def is_member(user, project, allow_draft):
    """return true if user is member of the project"""
    return (user in project.members.all()) and (
        (project.project_sites.current().status != "DRAFT") or allow_draft
    )  # noqa: F841


def in_allowed_departments(user, project):
    """return true if project is in allowed departments for user"""
    allowed = user.profile.departments.values_list("code", flat=True)
    if not allowed:  # empty list means full access
        return True
    return project.commune and (project.commune.department_id in allowed)


def get_project_moderators(site):
    """Return all project moderators for a given site"""
    return get_users_with_perms(
        site,
        with_group_users=True,
        only_with_perms_in=["moderate_projects"],
    )


def is_project_moderator(user, site):
    """Check if this user is allowed to moderate new projects"""
    return uv_utils.has_perm(user, "moderate_projects", site)


def is_project_moderator_or_403(user, site):
    if is_project_moderator(user, site):
        return True

    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_regional_actors_for_project(site, project, allow_national=False):
    """Return regional actors for a given site and project"""
    if not project.commune or not project.commune.department:
        return auth_models.User.objects.none()

    users = get_advisors(site)

    area_filter = Q(profile__departments=project.commune.department)
    if allow_national:
        area_filter = area_filter | Q(profile__departments=None)

    users = users.filter(area_filter)

    return users.distinct()


def get_national_actors(site):
    """Return national actors for a given site"""
    return get_advisors(site).filter(profile__departments=None).distinct()


def get_advisors(site):
    """Return advisors for given site"""
    group_name = uv_utils.make_group_name_for_site("advisor", site)
    return auth_models.User.objects.filter(groups__name=group_name)


def is_regional_actor_for_project(site, project, user, allow_national=False):
    """Check if this user is a regional actor for a given project"""
    return user in get_regional_actors_for_project(site, project, allow_national)


def check_if_national_actor(site, user):
    """Check if this user is a national actor"""
    return user in get_national_actors(site)


def is_regional_actor_for_project_or_403(site, project, user, allow_national=False):
    if is_regional_actor_for_project(site, project, user, allow_national):
        return True
    # TODO on met le raise sur un if not ?
    raise PermissionDenied("L'information demandée n'est pas disponible")


def get_switchtenders_for_project(project):
    """XXX Compatibility"""
    return get_advisors_for_project(project)


def get_advisors_for_project(project):
    """Return all the switchtenders for a given project"""
    return auth_models.User.objects.filter(
        projects_switchtended_per_site__project=project,
        projects_switchtended_per_site__site=get_current_site(request=None),
    ).distinct()


def get_advising_context_for_project(
    user: User, project: "Project"
) -> tuple["ProjectSwitchtender", dict[str, bool]]:
    try:
        advisor = models.ProjectSwitchtender.objects.get(
            switchtender=user, project=project, site=get_current_site(request=None)
        )
    except models.ProjectSwitchtender.DoesNotExist:
        return None, {
            "is_observer": False,
            "is_advisor": False,
        }

    return advisor, {
        "is_observer": advisor.is_observer,
        "is_advisor": not advisor.is_observer,
    }


def is_advisor_for_project(user: User, project: "Project") -> bool:
    return models.ProjectSwitchtender.objects.filter(
        switchtender=user, project=project, site=get_current_site(request=None)
    ).exists()


def get_collaborators_for_project(project):
    return project.members.all().distinct()


def get_notification_recipients_for_project(project):
    """Get all the people that should receive notifications for a given project"""
    return (
        get_switchtenders_for_project(project) | get_collaborators_for_project(project)
    ).distinct()


# ----------------------------------------------
# Notification helpers
# ----------------------------------------------


def notify_advisors_of_project(project, notification, exclude=None):
    """Dispatch notification to every advisor, on their reference Site"""
    for advisor in project.switchtender_sites.exclude(switchtender=exclude):
        notify.send(recipient=advisor.switchtender, site=advisor.site, **notification)


def notify_members_of_project(project, notification, exclude=None):
    """Dispatch notification to members, always on the project original Site"""
    original_site = project.project_sites.origin()
    recipients = project.members.all()
    if exclude:
        recipients = recipients.exclude(pk=exclude.pk)

    notify.send(
        recipient=recipients,
        site=original_site.site,
        **notification,
    )


def generate_ro_key():
    """Generate the ReadOnly key for sharing"""
    return uuid.uuid4().hex


def get_projects_for_user(user, site):
    memberships = models.ProjectMember.objects.filter(
        Q(project__sites=site),
        Q(project__deleted=None),
        Q(member=user),
        Q(is_owner=True)
        | Q(~Q(project__project_sites__status="DRAFT"), is_owner=False),
    )

    return [m.project for m in memberships.all()]


def refresh_user_projects_in_session(request, user):
    """store the user projects in the session"""

    site = get_current_site(request)

    projects = get_projects_for_user(user, site)

    request.session["projects"] = list(
        {
            "name": p.name,
            "id": p.id,
            "location": p.location,
            "commune": p.commune.name if p.commune else None,
            "inactive": bool(p.inactive_since),
            "actions_open": p.tasks.open().count(),
        }
        for p in projects
    )


def format_switchtender_identity(user):
    fmt = f"{user.first_name}"
    fmt += f" {user.last_name}"
    if user.profile and user.profile.organization:
        fmt += f" - {user.profile.organization.name}"

    return fmt


# eof
