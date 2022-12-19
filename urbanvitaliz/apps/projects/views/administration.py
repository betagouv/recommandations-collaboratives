# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""
from actstream import action
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz import utils
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.invites.forms import InviteForm

from .. import forms, models
from ..utils import (can_administrate_project, can_manage_or_403,
                     can_manage_project, is_regional_actor_for_project)

########################################################################
# Access
########################################################################


@login_required
def project_administration(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_manage_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    # Fetch pending invites
    pending_invites = []
    for invite in invites_models.Invite.on_site.filter(
        project=project, accepted_on=None
    ):
        pending_invites.append(invite)

    invite_form = InviteForm()

    if request.method == "POST":
        form = forms.ProjectForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_on = timezone.now()
            instance.save()
            form.save_m2m()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
        else:
            postcode = None
        project_form = forms.ProjectForm(
            instance=project, initial={"postcode": postcode}
        )

    return render(request, "projects/project/administration_panel.html", locals())


@login_required
def access_update(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_manage_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    # Fetch pending invites
    pending_invites = []
    for invite in invites_models.Invite.on_site.filter(
        project=project, accepted_on=None
    ):
        pending_invites.append(invite)

    if request.method == "POST":
        form = InviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            role = form.cleaned_data["role"]

            # Try to resolve email to a user first
            try:
                user = User.objects.get(username=email)
            except User.DoesNotExist:
                user = None

            already_invited = False
            already_member = False
            if user and user in project.members.all():
                already_member = True
            else:
                try:
                    already_invited = invites_models.Invite.on_site.filter(
                        project=project, email=email, role=role
                    ).exists()
                except invites_models.Invite.DoesNotExist:
                    pass

            # Already invited, skip
            if already_member or already_invited:
                messages.warning(
                    request,
                    "Cet usager ({0}) a déjà été invité, aucun courriel n'a été envoyé.".format(
                        email
                    ),
                )
                return render(request, "projects/project/access_update.html", locals())

            else:
                # New invite
                invite = form.save(commit=False)

                # Check if we are allowed to invite in case of an advisor's invite
                if invite.role == "SWITCHTENDER":
                    if not (
                        can_administrate_project(project, request.user)
                        or is_regional_actor_for_project(
                            project, request.user, allow_national=True
                        )
                    ):
                        raise PermissionDenied

                invite.project = project
                invite.inviter = request.user
                invite.site = request.site
                invite.save()

                # Add activity
                action.send(
                    invite.inviter,
                    verb="a invité un·e collaborateur·rice à rejoindre le projet",
                    action_object=invite,
                    target=invite.project,
                )

                # Do we already know this user?
                try:
                    invited_user = User.objects.get(email=email)
                except User.DoesNotExist:
                    invited_user = None

                # Dispatch notifications
                params = {
                    "sender": {
                        "first_name": request.user.first_name,
                        "last_name": request.user.last_name,
                        "email": request.user.email,
                    },
                    "message": invite.message,
                    "invite_url": utils.build_absolute_url(
                        invite.get_absolute_url(), auto_login_user=invited_user
                    ),
                    "project": digests.make_project_digest(project),
                }

                if request.user.profile:
                    if request.user.profile.organization:
                        params["sender"][
                            "organization"
                        ] = request.user.profile.organization.name

                send_email(
                    template_name="sharing invitation",
                    recipients=[{"email": email}],
                    params=params,
                )

                messages.success(
                    request,
                    "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                        email
                    ),
                    extra_tags=["email"],
                )
                return redirect(
                    reverse("projects-project-detail-overview", args=[project_id])
                )

            return redirect(reverse("projects-access-update", args=[project_id]))
    else:
        form = InviteForm()
    return render(request, "projects/project/access_update.html", locals())


@login_required
def access_delete(request, project_id: int, email: str):
    """Delete en email from the project ACL"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    if project.status == "DRAFT":
        raise PermissionDenied()

    membership = get_object_or_404(
        models.ProjectMember, project=project, member__username=email
    )

    can_manage_or_403(project, request.user)

    if request.method == "POST":
        if membership.is_owner:
            messages.error(
                request,
                "Vous ne pouvez pas retirer le propriétaire de son propre projet.",
                extra_tags=["auth"],
            )

        elif membership in project.projectmember_set.exclude(is_owner=True):
            project.members.remove(membership.member)
            messages.success(
                request,
                "{0} a bien été supprimé de la liste des participants.".format(email),
                extra_tags=["auth"],
            )

    return redirect(reverse("projects-access-update", args=[project_id]))


# eof
