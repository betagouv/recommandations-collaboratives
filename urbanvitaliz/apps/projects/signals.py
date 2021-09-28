import django.dispatch
from actstream import action
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

action_accepted = django.dispatch.Signal()
action_rejected = django.dispatch.Signal()
action_done = django.dispatch.Signal()
action_undone = django.dispatch.Signal()
