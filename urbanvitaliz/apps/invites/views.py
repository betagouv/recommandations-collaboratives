from django.contrib.auth import login
from django.contrib.auth import models as auth_models
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz.apps.addressbook import models as addressbook_models

from . import forms, models


def invite_accept(request, invite_id):
    invite = get_object_or_404(
        models.Invite, pk=invite_id, site=request.site, accepted_on=None
    )
    project = invite.project

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
            if existing_account == request.user:
                user = request.user
            else:
                return HttpResponseForbidden()

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
            # Now, grant the user her new rights
            if invite.role == "SWITCHTENDER":
                if user not in project.switchtenders.all():
                    project.switchtenders.add(user)
            else:
                if user.email not in project.emails:
                    project.emails.append(user.email)

            invite.accepted_on = timezone.now()
            invite.save()
            project.save()

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
                reverse("magicauth-login")
                + "?next="
                + reverse("invites-invite-details", args=(invite.pk,))
            )

    form = forms.InviteAcceptForm(request.GET or None)

    return render(request, "invites/invite_details.html", locals())
