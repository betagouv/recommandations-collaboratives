from actstream import action
from actstream.models import actor_stream
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from hijack.signals import hijack_started


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    if not (user.is_staff or hasattr(user, "is_hijacked")):
        action.send(user, verb="s'est connecté")


@receiver(hijack_started)
def delete_login_trace(sender, hijacker, hijacked, request, **kwargs):
    last_login = actor_stream(hijacked).last()
    if last_login:
        last_login.delete()
