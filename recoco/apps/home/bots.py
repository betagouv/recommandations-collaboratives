"""Rules for bot accounts (``UserProfile.is_bot``).

A bot authenticates with an API key only, which skips 2FA, so it must never
carry human privileges: no staff or superuser flag, no global Django
permission and no human role group (the groups that require 2FA). Rights are
given per site with guardian object permissions, or through groups that are
not human roles (e.g. ``<site>_trusted_bot``).
"""

from django.contrib.auth.models import Group

from recoco.apps.home.models import UserProfile

# groups that give human roles; they are also the ones that require 2FA
HUMAN_ROLE_GROUP_REGEX = r".*(staff|admin|advisor)$"

BOT_PRIVILEGE_ERROR = (
    "Un compte bot ne peut être ni staff, ni superutilisateur, ni avoir de "
    "permission globale, ni rejoindre un groupe staff, admin ou conseiller."
)


def is_bot(user_id):
    return (
        user_id is not None
        and UserProfile.objects.filter(user_id=user_id, is_bot=True).exists()
    )


def human_role_groups(groups):
    """The groups of ``groups`` (a Group queryset) that a bot cannot join."""
    return groups.filter(name__regex=HUMAN_ROLE_GROUP_REGEX)


def human_role_group_ids(group_ids):
    return set(
        human_role_groups(Group.objects.filter(pk__in=group_ids)).values_list(
            "pk", flat=True
        )
    )
