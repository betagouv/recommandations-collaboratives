"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

from actstream import action
from allauth.account.signals import user_logged_in as allauth_user_logged_in
from magicauth.signals import user_logged_in as magicauth_user_logged_in

from django.contrib.auth.models import update_last_login
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from recoco import verbs


def log_connection_on_user_login(sender, user, request, **kwargs):
    action.send(user, verb=verbs.User.LOGIN)


@receiver(user_logged_in)
def update_login_fields(sender, user, request, **kwargs):
    profile = user.profile
    profile.previous_login_at = user.last_login
    profile.save(update_fields=["previous_login_at"])

    # Call the original django handler
    update_last_login(sender, user, **kwargs)


allauth_user_logged_in.connect(log_connection_on_user_login)
magicauth_user_logged_in.connect(log_connection_on_user_login)

user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")


# eof
