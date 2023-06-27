"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

from actstream import action
from allauth.account.signals import user_logged_in as allauth_user_logged_in
from magicauth.signals import user_logged_in as magicauth_user_logged_in

from urbanvitaliz import verbs


def log_connection_on_user_login(sender, user, request, **kwargs):
    action.send(user, verb=verbs.User.LOGIN)


allauth_user_logged_in.connect(log_connection_on_user_login)
magicauth_user_logged_in.connect(log_connection_on_user_login)

# eof
