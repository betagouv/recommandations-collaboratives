from actstream import action
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    if not user.is_staff:
        action.send(user, verb="s'est connecté")
