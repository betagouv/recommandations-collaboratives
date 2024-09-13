# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.signals import user_logged_in
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import ensure_csrf_cookie
from notifications import models as notifications_models

from recoco import verbs
from recoco.apps.communication import constants as communication_constants
from recoco.apps.communication import digests
from recoco.apps.communication.api import send_email
from recoco.apps.communication.digests import normalize_user_name
from recoco.utils import (
    check_if_advisor,
    get_site_config_or_503,
    has_perm_or_403,
    is_staff_for_site,
)

from .. import forms, models, signals
from ..utils import (
    assign_advisor,
    assign_collaborator,
    assign_observer,
    can_administrate_project,
    get_active_project,
    is_advisor_for_project,
    is_project_moderator_or_403,
    is_regional_actor_for_project_or_403,
    refresh_user_projects_in_session,
    set_active_project_id,
    unassign_advisor,
)

__all__ = ["rest", "feeds", "notes", "sharing", "tasks", "documents"]


# ----
# Utils
# ----
def mark_general_notifications_as_seen(user):
    # Mark some notifications as seen
    project_ct = ContentType.objects.get_for_model(models.Project)
    # FIXME update filter to current verbs
    notif_verbs = [verbs.Project.AVAILABLE, verbs.Project.SUBMITTED_BY]
    notifications = user.notifications.unread().filter(
        verb__in=notif_verbs,
        target_content_type=project_ct.pk,
    )
    notifications.mark_all_as_read()


# -----
# Project Moderation
# -----
@login_required
def project_moderation_list(request):
    is_project_moderator_or_403(request.user, request.site)

    site_config = get_site_config_or_503(request.site)

    draft_projects = models.Project.on_site.filter(
        project_sites__status="DRAFT", project_sites__site=request.site, deleted=None
    ).order_by("-created_on")

    return render(request, "projects/projects_moderation.html", locals())


@login_required
def project_moderation_refuse(request, project_pk):
    is_project_moderator_or_403(request.user, request.site)

    project = get_object_or_404(
        models.Project.on_site,
        project_sites__status="DRAFT",
        project_sites__site=request.site,
        deleted=None,
        pk=project_pk,
    )

    if request.method == "POST":
        project.project_sites.filter(site=request.site).update(status="REJECTED")
        project.updated_on = timezone.now()
        project.save()

        messages.add_message(
            request, messages.INFO, f"Le projet '{project.name}' a été refusé."
        )

    return redirect(reverse("projects-moderation-list"))


@login_required
def project_moderation_accept(request, project_pk):
    is_project_moderator_or_403(request.user, request.site)

    project = get_object_or_404(
        models.Project.on_site,
        project_sites__status="DRAFT",
        project_sites__site=request.site,
        deleted=None,
        pk=project_pk,
    )

    if request.method == "POST":
        project.project_sites.filter(site=request.site).update(status="TO_PROCESS")
        project.updated_on = timezone.now()
        project.save()

        messages.add_message(
            request, messages.SUCCESS, f"Le projet '{project.name}' a été accepté."
        )

        signals.project_validated.send(
            sender=models.Project,
            site=request.site,
            moderator=request.user,
            project=project,
        )

        owner = project.owner
        if owner:
            # Update owner permissions now the project is no in DRAFT state anymore
            assign_collaborator(owner, project, is_owner=True)

            # Send an email to the project owner
            params = {
                "project": digests.make_project_digest(project, owner),
            }
            send_email(
                template_name=communication_constants.TPL_PROJECT_ACCEPTED,
                recipients=[
                    {
                        "name": normalize_user_name(owner),
                        "email": project.owner.email,
                    }
                ],
                params=params,
            )

        form = forms.ProjectModerationForm(request.POST)
        if form.is_valid():
            join = form.cleaned_data["join"]

            if join:
                # Assign current user as observer if requested
                assign_observer(request.user, project, request.site)
                messages.add_message(
                    request,
                    messages.INFO,
                    f"Vous êtes maintenant observateur·rice du projet '{project.name}'.",
                )

        return redirect(reverse("projects-project-detail-overview", args=(project.pk,)))

    return redirect(reverse("projects-moderation-list"))


# ----
# List, dashboards
# ----
@login_required
def project_list(request):
    if is_staff_for_site(request.user, request.site):
        return redirect("projects-project-list-staff")

    if check_if_advisor(request.user, request.site) or can_administrate_project(
        project=None, user=request.user
    ):
        return redirect("projects-project-list-advisor")

    raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")


@login_required
@ensure_csrf_cookie
@never_cache
def project_list_for_advisor(request):
    """Return the projects for the advisor"""
    if not (
        check_if_advisor(request.user, request.site)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    # unread_notifications = notifications_models.Notification.on_site.unread().filter(
    #    recipient=request.user, public=True
    # )

    mark_general_notifications_as_seen(request.user)

    project_ct = ContentType.objects.get_for_model(models.Project)
    user_project_pks = list(
        request.user.project_states.filter(
            project__switchtenders=request.user
        ).values_list("project__pk", flat=True)
    )

    action_stream = (
        request.user.notifications.filter(
            target_content_type=project_ct,
            target_object_id__in=user_project_pks,
        )
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:20]
    )

    return render(request, "projects/project/personal_advisor_dashboard.html", locals())


@login_required
@ensure_csrf_cookie
def project_list_for_staff(request):
    """
    Return the projects for the staff (and for other people as a fallback until the
    new dashboard is fully completed).
    """
    if not (
        check_if_advisor(request.user, request.site)
        or can_administrate_project(project=None, user=request.user)
        or is_staff_for_site(request.user, request.site)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    site_config = get_site_config_or_503(request.site)

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=True)
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:100]
    )

    mark_general_notifications_as_seen(request.user)

    return render(request, "projects/project/list-kanban.html", locals())


@login_required
@ensure_csrf_cookie
def project_maplist(request):
    """Return the projects for the switchtender as a map"""
    if not (
        check_if_advisor(request.user)
        or can_administrate_project(project=None, user=request.user)
    ):
        raise PermissionDenied("Vous n'avez pas le droit d'accéder à ceci.")

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=True)
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:100]
    )

    return render(request, "projects/project/list-map.html", locals())


# ----
# Joining projects
# ----
@login_required
def project_switchtender_join(request, project_id=None):
    """Join as switchtender"""

    project = get_object_or_404(models.Project, pk=project_id)

    if not can_administrate_project(project, request.user):
        is_regional_actor_for_project_or_403(
            get_current_site(request), project, request.user, allow_national=True
        )

    if request.method == "POST":
        assign_advisor(request.user, project)

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "TODO"},
        )
        if not created:
            personal_status.status = "TODO"
            personal_status.save()

        project.updated_on = timezone.now()
        project.save()

        signals.project_switchtender_joined.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_observer_join(request, project_id=None):
    """Join as observer"""
    project = get_object_or_404(models.Project, pk=project_id)

    if not can_administrate_project(project, request.user):
        is_regional_actor_for_project_or_403(
            get_current_site(request), project, request.user, allow_national=True
        )

    if request.method == "POST":
        assign_observer(request.user, project)

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "TODO"},
        )
        if not created:
            personal_status.status = "TODO"
            personal_status.save()

        project.updated_on = timezone.now()
        project.save()

        signals.project_observer_joined.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_switchtender_leave(request, project_id=None):
    """Leave switchtender"""
    project = get_object_or_404(models.Project, pk=project_id)

    if not is_advisor_for_project(request.user, project):
        raise PermissionDenied()

    if request.method == "POST":
        unassign_advisor(request.user, project)
        project.updated_on = timezone.now()
        project.save()

        personal_status, created = models.UserProjectStatus.objects.get_or_create(
            site=request.site,
            user=request.user,
            project=project,
            defaults={"status": "NOT_INTERESTED"},
        )
        if not created:
            personal_status.status = "NOT_INTERESTED"
            personal_status.save()

        signals.project_switchtender_leaved.send(sender=request.user, project=project)

    return redirect(reverse("projects-project-detail", args=[project_id]))


@login_required
def project_delete(request, project_id=None):
    """Mark project as deleted in the DB"""
    has_perm_or_403(request.user, "sites.delete_projects", request.site)

    project = get_object_or_404(models.Project, pk=project_id)
    if request.method == "POST":
        project.deleted = project.updated_on = timezone.now()
        project.save()
    return redirect(reverse("projects-project-list"))


########################################################################
# Login methods and signals
########################################################################
@receiver(user_logged_in)
def post_login_set_active_project(sender, user, request, **kwargs):
    # store my projects in the session
    refresh_user_projects_in_session(request, user)

    # Needed since get_active_project expects a user attribute
    request.user = user

    active_project = get_active_project(request)

    if not active_project:
        # Try to fetch a project
        active_project = models.Project.on_site.filter(members=user).first()
        if active_project:
            set_active_project_id(request, active_project.id)


# eof
