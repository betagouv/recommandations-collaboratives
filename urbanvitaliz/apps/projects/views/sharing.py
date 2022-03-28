# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django import forms
from django.contrib import messages
from django.contrib.auth import models as auth_models
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from urbanvitaliz.apps.communication.api import send_email

from .. import digests, models
from ..utils import can_manage_or_403


########################################################################
# Access
########################################################################
class AccessAddForm(forms.Form):
    """A form to add an Access"""

    email = forms.EmailField()


@login_required
def access_update(request, project_id):
    """Handle ACL for a project"""
    project = get_object_or_404(models.Project, pk=project_id)

    can_manage_or_403(project, request.user)

    # Compute who has created an account yet
    accepted_invites = []
    for email in project.emails:
        if auth_models.User.objects.filter(email=email).exists():
            accepted_invites.append(email)

    if request.method == "POST":
        form = AccessAddForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            if email not in project.emails:
                project.emails.append(email)
                project.save()
                messages.success(
                    request,
                    "Un courriel d'invitation à rejoindre le projet a été envoyé à {0}.".format(
                        email
                    ),
                    extra_tags=["email"],
                )

                send_email(
                    template_name="sharing invitation",
                    recipients=[{"email": email}],
                    params={
                        "sender": {"email": request.user.email},
                        "project": digests.make_project_digest(project),
                    },
                )

            return redirect(reverse("projects-access-update", args=[project_id]))
    else:
        form = AccessAddForm()
    return render(request, "projects/project/access_update.html", locals())


@login_required
def access_delete(request, project_id: int, email: str):
    """Delete en email from the project ACL"""
    project = get_object_or_404(models.Project, pk=project_id)

    can_manage_or_403(project, request.user)

    if request.method == "POST":
        if email == project.email:
            messages.error(
                request,
                "Vous ne pouvez pas retirer le propriétaire de son propre projet.",
                extra_tags=["auth"],
            )

        elif email in project.emails:
            project.emails.remove(email)
            project.save()
            messages.success(
                request,
                "{0} a bien été supprimé de la liste des collaborateurs.".format(email),
                extra_tags=["auth"],
            )

    return redirect(reverse("projects-access-update", args=[project_id]))


# eof
