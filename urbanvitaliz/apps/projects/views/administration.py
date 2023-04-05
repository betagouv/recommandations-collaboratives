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
from guardian.shortcuts import get_user_perms
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.invites.api import (
    invite_collaborator_on_project,
    invite_resend,
    invite_revoke,
)
from urbanvitaliz.apps.invites.forms import InviteForm
from urbanvitaliz.utils import has_perm_or_403, is_staff_for_site

from .. import forms, models
from ..utils import (
    is_regional_actor_for_project,
    unassign_advisor,
    unassign_collaborator,
)


########################################################################
# Access
########################################################################


@login_required
def project_administration(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    required_perms = (
        "invite_collaborators",
        "invite_advisors",
        "manage_collaborators",
        "manage_advisors",
        "change_project",
    )

    has_any_required_perm = any(
        user_perm in required_perms
        for user_perm in get_user_perms(request.user, project)
    )

    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    if not (
        is_regional_actor or has_any_required_perm or is_staff_for_site(request.user)
    ):
        raise PermissionDenied("L'information demandée n'est pas disponible")

    # Fetch pending invites
    pending_invites = []
    for invite in invites_models.Invite.on_site.filter(
        project=project, accepted_on=None
    ):
        pending_invites.append(invite)

    invite_form = InviteForm()

    if request.method == "POST":
        # Allow staff of current site or users with perm
        is_staff_for_site(request.user, request.site) or has_perm_or_403(
            request.user, "change_project", project
        )

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


@login_required
@require_http_methods(["POST"])
def access_revoke_invite(request, project_id, invite_id):
    """Revoke an invitation for a collectivity member"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    invite = get_object_or_404(invites_models.Invite, pk=invite_id, accepted_on=None)

    if not is_staff_for_site(request.user):
        if invite.role == "SWITCHTENDER":
            has_perm_or_403(request.user, "manage_advisors", project)
        else:
            has_perm_or_403(request.user, "manage_collaborators", project)

    if invite_revoke(invite):
        messages.success(
            request,
            "L'invitation de {0} a bien été supprimée.".format(invite.email),
            extra_tags=["auth"],
        )
    else:
        messages.error(
            request,
            "Désolé, nous n'avons pas pu supprimer l'invitation de {0}.".format(
                invite.email
            ),
            extra_tags=["auth"],
        )

    return redirect(reverse("projects-project-administration", args=[project_id]))


##############################################################################
# Collectivity
##############################################################################


@login_required
@require_http_methods(["POST"])
def access_collaborator_invite(request, project_id):
    """Invite a collectivity member"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # can also be a regional actor.
    # FIXME: should we still use allow_national or move to is_staff_for_site?
    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    if not is_staff_for_site(request.user):
        is_regional_actor or has_perm_or_403(
            request.user, "invite_collaborators", project
        )

    return access_invite(request, "COLLABORATOR", project)


@login_required
@require_http_methods(["POST"])
def access_collaborator_resend_invite(request, project_id, invite_id):
    """Resend invitation for a collectivity member"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # can also be regional actor
    # FIXME: should we still use allow_national or move to is_staff_for_site?
    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    if not is_staff_for_site(request.user):
        is_regional_actor or has_perm_or_403(
            request.user, "invite_collaborators", project
        )

    invite = get_object_or_404(
        invites_models.Invite, role="COLLABORATOR", pk=invite_id, accepted_on=None
    )

    if invite_resend(invite):
        messages.success(
            request,
            f"{invite.email} a bien été relancé par courriel.",
            extra_tags=["auth"],
        )
    else:
        messages.error(
            request,
            f"Désolé, nous n'avons pas pu relancer {invite.email} par courriel.",
            extra_tags=["auth"],
        )

    return redirect(reverse("projects-project-administration", args=[project_id]))


@login_required
@require_http_methods(["POST"])
def access_collaborator_delete(request, project_id: int, email: str):
    """Delete a collectivity member from the project ACL"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    if not is_staff_for_site(request.user):
        has_perm_or_403(request.user, "manage_collaborators", project)

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
            unassign_collaborator(membership.member, project)
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

    # can also be regional actor
    # FIXME: should we still use allow_national or move to is_staff_for_site?
    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    if not is_staff_for_site(request.user):
        is_regional_actor or has_perm_or_403(request.user, "invite_advisors", project)

    return access_invite(
        request, "SWITCHTENDER", project
    )  # should we keep switchtender?


@login_required
@require_http_methods(["POST"])
def access_advisor_resend_invite(request, project_id, invite_id):
    """Resend invitation for an advisor"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)

    # can also be regional actor
    # FIXME: should we still use allow_national or move to is_staff_for_site?
    is_regional_actor = is_regional_actor_for_project(
        request.site, project, request.user, allow_national=True
    )

    if not is_staff_for_site(request.user):
        is_regional_actor or has_perm_or_403(request.user, "invite_advisors", project)

    invite = get_object_or_404(
        invites_models.Invite, role="SWITCHTENDER", pk=invite_id, accepted_on=None
    )  # should we keep switchtender?

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

    if not is_staff_for_site(request.user):
        has_perm_or_403(request.user, "manage_advisors", project)

    advisor = get_object_or_404(
        models.ProjectSwitchtender,
        project=project,
        switchtender__username=email,
        site=request.site,
    )

    unassign_advisor(request.user, project, request.site)

    messages.success(
        request,
        "{0} a bien été supprimé de la liste des conseiller·e·s.".format(email),
        extra_tags=["auth"],
    )

    return redirect(reverse("projects-project-administration", args=[project_id]))


# eof
