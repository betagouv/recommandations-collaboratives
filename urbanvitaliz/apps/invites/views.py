from django.contrib.auth import login
from django.contrib.auth import models as auth_models
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.projects import signals as projects_signals
from urbanvitaliz.apps.projects.utils import assign_collaborator, assign_advisor

from . import forms, models


def invite_accept(request, invite_id):
    invite = get_object_or_404(
        models.Invite, pk=invite_id, site=request.site, accepted_on=None
    )
    project = invite.project

    current_site = request.site

    # Check if this email already exists as an account
    existing_account = None
    try:
        existing_account = auth_models.User.objects.get(email=invite.email)
    except auth_models.User.DoesNotExist:
        pass

    if request.method == "POST":
        form = forms.InviteAcceptForm(request.POST)
        user = None

        if existing_account:
            if existing_account != request.user:
                return HttpResponseForbidden()
            user = request.user

        # New account
        else:
            # we shouldn't be logged in at this point
            if request.user.is_authenticated:
                return HttpResponseForbidden()

            if form.is_valid():
                user = auth_models.User.objects.create(
                    username=invite.email,
                    email=invite.email,
                    first_name=form.cleaned_data.get("first_name"),
                    last_name=form.cleaned_data.get("last_name"),
                )

                organization, _ = addressbook_models.Organization.objects.get_or_create(
                    name=form.cleaned_data.get("organization")
                )

                user.profile.organization = organization
                user.profile.organization_position = form.cleaned_data.get("position")

                user.profile.save()

                login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )

        if user:
            # user now has access to site
            user.profile.sites.add(current_site)

            # Now, grant the user her new rights
            if invite.role == "SWITCHTENDER":
                if assign_advisor(user, project, current_site):
                    projects_signals.project_switchtender_joined.send(
                        sender=request.user, project=project
                    )
            else:
                if assign_collaborator(user, project):
                    projects_signals.project_member_joined.send(
                        sender=request.user, project=project
                    )

            invite.accepted_on = timezone.now()
            invite.save()

            return redirect(project.get_absolute_url())

    return redirect(reverse("invites-invite-details", args=(invite.pk,)))


def invite_details(request, invite_id):
    invite = get_object_or_404(
        models.Invite, site=request.site, pk=invite_id, accepted_on=None
    )

    # Check if this email already exists as an account
    existing_account = None
    try:
        existing_account = auth_models.User.objects.get(email=invite.email)
    except auth_models.User.DoesNotExist:
        pass

    error_msg = None

    project = invite.project

    # Are we currently logged in and usurpating a link?
    if request.user.is_authenticated:
        if not existing_account or (existing_account != request.user):
            error_msg = "Désolé, cette invitation ne semble pas vous concerner."
            return render(request, "invites/invite_error.html", locals())
    else:
        if existing_account:  # An account already exists, go to login first
            return redirect(
                reverse("account_login")
                + "?next="
                + reverse("invites-invite-details", args=(invite.pk,))
            )

    form = forms.InviteAcceptForm(request.GET or None)

    return render(request, "invites/invite_details.html", locals())
