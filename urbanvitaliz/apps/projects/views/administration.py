# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""
from actstream import action
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.invites.api import (invite_collaborator_on_project,
                                           invite_resend)
from urbanvitaliz.apps.invites.forms import InviteForm

from .. import forms, models
from ..utils import (can_administrate_or_403, can_administrate_project,
                     can_manage_project, is_regional_actor_for_project)

########################################################################
# Access
########################################################################


@login_required
def project_administration(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not can_administrate_project(project, request.user):
        raise PermissionDenied

    can_administrate = can_administrate_project(project, request.user)

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

            try:
                commune = geomatics_models.Commune.objects.get(
                    insee=form.cleaned_data["insee"]
                )
                instance.commune = commune
            except geomatics_models.Commune.DoesNotExist:
                pass

            instance.updated_on = timezone.now()
            instance.save()
            form.save_m2m()
            return redirect(reverse("projects-project-detail", args=[project_id]))
    else:
        if project.commune:
            postcode = project.commune.postal
            insee = project.commune.insee
        else:
            postcode = None
            insee = None
        project_form = forms.ProjectForm(
            instance=project,
            initial={"postcode": postcode, "insee": insee},
        )

    return render(request, "projects/project/administration_panel.html", locals())


def access_invite(request, role, project):
    """Generic function to invite a member. NOT to be exposed"""
    form = InviteForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        invite = invite_collaborator_on_project(
            request.site,
            project,
            role,
            email,
            message,
            request.user,
        )

        if invite:
            action.send(
                invite.inviter,
                verb="a invité un·e collaborateur·rice à rejoindre le projet",
                action_object=invite,
                target=invite.project,
            )
            messages.success(
                request,
                "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                    email
                ),
                extra_tags=["email"],
            )
        else:
            messages.warning(
                request,
                "Cet usager ({0}) n'a pu être invité, aucun courriel n'a été envoyé. Vérifiez qu'il n'est pas déjà invité ou membre".format(
                    email
                ),
            )

    source = request.POST.get("source")
    if source == "admin":
        return redirect(reverse("projects-project-administration", args=[project.pk]))

    return redirect(reverse("projects-project-detail-overview", args=[project.pk]))


##############################################################################
# Collectivity
##############################################################################
@login_required
@require_http_methods(["POST"])
def access_collectivity_invite(request, project_id):
    """Invite a collectivity member"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_manage_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    return access_invite(request, "COLLABORATOR", project)


@login_required
@require_http_methods(["POST"])
def access_collectivity_resend_invite(request, project_id, invite_id):
    """Resend invitation for an advisor"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_manage_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    invite = get_object_or_404(
        invites_models.Invite, role="COLLABORATOR", pk=invite_id, accepted_on=None
    )

    if invite_resend(invite):
        messages.success(
            request,
            "{0} a bien été relancé par courriel.".format(invite.email),
            extra_tags=["auth"],
        )
    else:
        messages.error(
            request,
            "Désolé, nous n'avons pas pu relancer {0} par courriel.".format(
                invite.email
            ),
            extra_tags=["auth"],
        )

    return redirect(reverse("projects-project-administration", args=[project_id]))


@login_required
@require_http_methods(["POST"])
def access_collectivity_delete(request, project_id: int, email: str):
    """Delete a collectivity member from the project ACL"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    can_administrate_or_403(project, request.user)

    membership = get_object_or_404(
        models.ProjectMember, project=project, member__username=email
    )

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

    return redirect(reverse("projects-project-administration", args=[project_id]))


##############################################################################
# Advisors
##############################################################################


@login_required
@require_http_methods(["POST"])
def access_advisor_invite(request, project_id):
    """Invite an advisor"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_administrate_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    return access_invite(request, "SWITCHTENDER", project)


@login_required
@require_http_methods(["POST"])
def access_advisor_resend_invite(request, project_id, invite_id):
    """Resend invitation for an advisor"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    if not (
        can_administrate_project(project, request.user)
        or is_regional_actor_for_project(project, request.user, allow_national=True)
    ):
        raise PermissionDenied

    invite = get_object_or_404(
        invites_models.Invite, role="SWITCHTENDER", pk=invite_id, accepted_on=None
    )

    if invite_resend(invite):
        messages.success(
            request,
            "{0} a bien été relancé par courriel.".format(invite.email),
            extra_tags=["auth"],
        )
    else:
        messages.error(
            request,
            "Désolé, nous n'avons pas pu relancer {0} par courriel.".format(
                invite.email
            ),
            extra_tags=["auth"],
        )

    return redirect(reverse("projects-project-administration", args=[project_id]))


@login_required
@require_http_methods(["POST"])
def access_advisor_delete(request, project_id: int, email: str):
    """Delete an advisor from the project ACL"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    can_administrate_or_403(project, request.user)

    advisor = get_object_or_404(
        models.ProjectSwitchtender,
        project=project,
        switchtender__username=email,
        site=request.site,
    )

    advisor.delete()

    messages.success(
        request,
        "{0} a bien été supprimé de la liste des conseiller·e·s.".format(email),
        extra_tags=["auth"],
    )

    return redirect(reverse("projects-project-administration", args=[project_id]))


# eof
