"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

import sentry_sdk
from actstream import action
from allauth.account.signals import user_logged_in as allauth_user_logged_in
from allauth.account.signals import user_signed_up as allauth_user_signed_up
from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site
from django.db.models.signals import post_save
from django.dispatch import receiver
from magicauth.signals import user_logged_in as magicauth_user_logged_in

from recoco import verbs
from recoco.apps.home.models import UserProfile
from recoco.apps.projects.utils import refresh_user_projects_in_session


def log_connection_on_user_login(sender, user, request, **kwargs):
    action.send(user, verb=verbs.User.LOGIN)


@receiver(user_logged_in)
def update_login_fields(sender, user, request, **kwargs):
    refresh_user_projects_in_session(request, user)

    # Call the original django handler
    update_last_login(sender, user, **kwargs)

    # Add the current site so that the user can access all the features
    user.profile.sites.add(get_current_site(request))


allauth_user_logged_in.connect(log_connection_on_user_login)
magicauth_user_logged_in.connect(log_connection_on_user_login)

user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")


@receiver(allauth_user_signed_up)
def post_signup_workflow(sender, request, user, **kwargs):
    pass


@receiver(post_save, sender=UserProfile)
def watch_organisation_to_understand_mystery(instance: UserProfile, **kwargs):
    if getattr(instance.organization, "id", None) == 781:
        text = (
            f"User {instance.user.id} was assigned to mysterious organization 'Mairie'"
        )
        sentry_sdk.capture_exception(Exception(text))
        print(text)


# eof
