"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

from actstream import action
from allauth.account.signals import user_logged_in as allauth_user_logged_in
from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.sites.shortcuts import get_current_site
from django.dispatch import receiver
from magicauth.signals import user_logged_in as magicauth_user_logged_in

from recoco import verbs
from recoco.apps.projects.utils import refresh_user_projects_in_session

from .models import UserLoginEntry


def log_connection_on_user_login(sender, user, request, **kwargs):
    action.send(user, verb=verbs.User.LOGIN)


@receiver(user_logged_in)
def update_login_fields(sender, user, request, **kwargs):
    profile = user.profile
    profile.previous_login_at = user.last_login
    profile.save(update_fields=["previous_login_at"])

    current_site = get_current_site(request)

    UserLoginEntry.objects.create(
        profile=user.profile,
        site=current_site,
        action=UserLoginEntry.ACTION_LOGGED_IN,
        ip=request.META.get("REMOTE_ADDR"),
    )

    refresh_user_projects_in_session(request, user)

    # Call the original django handler
    update_last_login(sender, user, **kwargs)

    # Add the current site so that the user can access all the features
    user.profile.sites.add(current_site)


@receiver(user_logged_out)
def on_logout(sender, user, request, **kwargs):
    UserLoginEntry.objects.create(
        profile=user.profile,
        site=get_current_site(request),
        action=UserLoginEntry.ACTION_LOGGED_OUT,
        ip=request.META.get("REMOTE_ADDR"),
    )


allauth_user_logged_in.connect(log_connection_on_user_login)
magicauth_user_logged_in.connect(log_connection_on_user_login)

user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")


# eof
