from actstream import action
from allauth.account.signals import user_logged_in as allauth_user_logged_in
from magicauth.signals import user_logged_in as magicauth_user_logged_in


def log_connection_on_user_login(sender, user, request, **kwargs):
    action.send(user, verb="s'est connecté")


allauth_user_logged_in.connect(log_connection_on_user_login)
magicauth_user_logged_in.connect(log_connection_on_user_login)
