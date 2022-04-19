from django.contrib.auth import models as auth_models
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from . import forms, models


def invite_accept(request, invite_id):
    invite = get_object_or_404(models.Invite, pk=invite_id, accepted_on=None)

    if request.method == "POST":
        if invite.role == "SWITCHTENDER":
            if existing_account not in project.switchtenders:
                project.switchtenders.add(existing_account)

                invite.accepted_on = timezone.now()
                invite.save()

        return redirect(project.get_absolute_url())

    return redirect(reverse("invites-invite-details", args=(invite.pk)))


def invite_details(request, invite_id):
    invite = get_object_or_404(models.Invite, pk=invite_id, accepted_on=None)

    # Check if this email already exists as an account
    existing_account = None
    try:
        existing_account = auth_models.User.objects.get(email=invite.email)
    except auth_models.User.DoesNotExist:
        pass

    error_msg = None

    project = invite.project

    # Are we currently logged in and usurping a link?
    if request.user.is_authenticated:
        if not existing_account or (existing_account != request.user):
            error_msg = "Désolé, cette invitation ne semble pas vous concerner."
            return render(request, "invites/invite_error.html", locals())
    else:
        if existing_account:  # An account already exists, go to login first
            return redirect(
                reverse("magicauth-login")
                + "?next="
                + reverse("invites-invite-details", args=(invite.pk))
            )

    form = forms.InviteAcceptForm(request.GET or None)

    return render(request, "invites/invite_details.html", locals())
