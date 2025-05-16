from django import template

from recoco.apps.invites.models import Invite

register = template.Library()


@register.simple_tag
def pending_invitations_for(user):
    """Return a list of projects tagged with the given tag"""
    return Invite.objects.pending().filter(email=user.username)
