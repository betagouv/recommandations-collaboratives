# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urbanvitaliz import utils
from urbanvitaliz.apps.communication import digests
from urbanvitaliz.apps.communication.api import send_email
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.invites.forms import InviteForm
from urbanvitaliz.apps.survey import models as survey_models

from .. import models
from ..utils import can_manage_or_403, can_manage_project

########################################################################
# Access
########################################################################


@login_required
def access_update(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, sites=request.site, pk=project_id)
    can_manage_or_403(project, request.user)

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
                    "Cet usager ({0}) a déjà été invité, aucun courrier n'a été envoyé.".format(
                        email
                    ),
                )
                return render(request, "projects/project/access_update.html", locals())

            else:
                # New invite
                invite = form.save(commit=False)
                invite.project = project
                invite.inviter = request.user
                invite.site = request.site
                invite.save()

                send_email(
                    template_name="sharing invitation",
                    recipients=[{"email": email}],
                    params={
                        "sender": {"email": request.user.email},
                        "invite_url": utils.build_absolute_url(
                            invite.get_absolute_url()
                        ),
                        "project": digests.make_project_digest(project),
                    },
                )

                messages.success(
                    request,
                    "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                        email
                    ),
                    extra_tags=["email"],
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


def project_detail_from_sharing_link(request, project_ro_key):
    """Return a special view of the project using the sharing link"""
    try:
        project = models.Project.on_site.get(ro_key=project_ro_key)
    except Exception:
        raise Http404()

    try:
        site_config = utils.get_site_config_or_503(request.site)
        session, created = survey_models.Session.objects.get_or_create(
            project=project, survey=site_config.project_survey
        )
    except Exception:
        pass

    can_manage = can_manage_project(project, request.user)

    return render(request, "projects/project/detail-ro.html", locals())


# eof
