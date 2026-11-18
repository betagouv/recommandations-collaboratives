"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

import re

import sentry_sdk
from actstream import action
from allauth.account.models import EmailAddress
from allauth.account.signals import user_signed_up as allauth_user_signed_up
from allauth.mfa.models import Authenticator
from allauth.mfa.signals import authenticator_added, authenticator_removed
from django.contrib.auth.models import Group, User, update_last_login
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Subquery, Value
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from recoco import verbs
from recoco.apps.home.bots import (
    BOT_PRIVILEGE_ERROR,
    HUMAN_ROLE_GROUP_REGEX,
    human_role_group_ids,
    human_role_groups,
    is_bot,
)
from recoco.apps.home.models import UserProfile
from recoco.apps.projects.utils import refresh_user_projects_in_session


@receiver(user_logged_in)
def update_login_fields(sender, user, request, **kwargs):
    refresh_user_projects_in_session(request, user)

    if getattr(request.resolver_match, "app_name", None) != "hijack":
        if not user.is_staff:
            action.send(user, verb=verbs.User.LOGIN)

        # Call the original django handler
        update_last_login(sender, user, **kwargs)

        # Add the current site so that the user can access all the features
        user.profile.sites.add(get_current_site(request))


user_logged_in.disconnect(update_last_login, dispatch_uid="update_last_login")


@receiver(allauth_user_signed_up)
def post_signup_workflow(sender, request, user, **kwargs):
    pass


@receiver(pre_save, sender=UserProfile)
def watch_organisation_to_understand_mystery(instance: UserProfile, **kwargs):
    previous = UserProfile.objects.filter(id=instance.id).first()
    if previous and previous.organization == instance.organization:
        return

    if getattr(instance.organization, "id", None) == 781:
        text = (
            f"User {instance.user.id} was assigned to mysterious organization 'Mairie'"
        )
        sentry_sdk.capture_exception(Exception(text))
        print(text)


@receiver(post_save, sender=UserProfile)
def disable_human_login_for_bots(sender, instance: UserProfile, **kwargs):
    """A bot only authenticates with an API key: no password, no email.

    Without an email, login by code, password reset and ProConnect
    cannot reach the account either.
    """
    if not instance.is_bot:
        return

    user = instance.user
    changed_privileges = _strip_human_privileges(user)
    if _strip_human_credentials(user) or changed_privileges:
        user.save(update_fields=["password", "email", "is_staff", "is_superuser"])

    EmailAddress.objects.filter(user=user).delete()
    # a bot key skips 2FA: it cannot keep human rights from a previous life
    user.user_permissions.clear()
    user.groups.remove(*human_role_groups(user.groups.all()))


def _strip_human_privileges(user):
    """Drop staff and superuser flags from a bot; return whether anything changed."""
    if not (user.is_staff or user.is_superuser):
        return False
    user.is_staff = False
    user.is_superuser = False
    return True


def _strip_human_credentials(user):
    """Drop password and email from a bot; return whether anything changed."""
    if not (user.has_usable_password() or user.email):
        return False
    user.set_unusable_password()
    user.email = ""
    return True


@receiver(pre_save, sender=User)
def keep_bots_without_human_credentials(sender, instance: User, **kwargs):
    """Saving a bot, e.g. from the user admin, cannot give it back a password
    or an email (the profile signal above only runs when the profile is saved).
    """
    if not is_bot(instance.pk):
        return

    _strip_human_credentials(instance)
    if instance.is_staff or instance.is_superuser:
        raise ValidationError(BOT_PRIVILEGE_ERROR)


@receiver(post_save, sender=EmailAddress)
def keep_bots_without_email_address(sender, instance: EmailAddress, **kwargs):
    """An email address would open login by code, password reset and ProConnect."""
    if is_bot(instance.user_id):
        instance.delete()


@receiver(m2m_changed, sender=User.groups.through)
def keep_bots_out_of_human_role_groups(
    sender, instance, action, reverse, pk_set, **kwargs
):
    """A bot key skips 2FA, so a bot cannot join a group that requires it."""
    if action != "pre_add":
        return

    if not reverse:  # user.groups.add(...)
        if is_bot(instance.pk) and human_role_group_ids(pk_set):
            raise ValidationError(BOT_PRIVILEGE_ERROR)
        return

    # group.user_set.add(...)
    if (
        human_role_group_ids([instance.pk])
        and UserProfile.objects.filter(user_id__in=pk_set, is_bot=True).exists()
    ):
        raise ValidationError(BOT_PRIVILEGE_ERROR)


@receiver(m2m_changed, sender=User.user_permissions.through)
def keep_bots_without_global_permissions(
    sender, instance, action, reverse, pk_set, **kwargs
):
    """Global permissions apply to every site: bots get per-site object
    permissions instead."""
    if action != "pre_add":
        return

    user_ids = pk_set if reverse else {instance.pk}
    if UserProfile.objects.filter(user_id__in=user_ids, is_bot=True).exists():
        raise ValidationError(BOT_PRIVILEGE_ERROR)


@receiver(m2m_changed, sender=User.groups.through)
def ensure_2fa_requirement(sender, instance, **kwargs):
    signal_action = kwargs.get("action")  # add/remove/clear
    reverse = kwargs["reverse"]  # change made from group.users not user.groups
    requires_2fa = Value(False)

    # user.groups.clear: the user is the only one affected so we only update them
    if signal_action == "post_clear" and not reverse:
        instance.profile.requires_2fa = False
        instance.profile.save()
        return

    user_profile_qs = UserProfile.objects.none()
    group_regex = HUMAN_ROLE_GROUP_REGEX

    # user.groups.add/remove and group.users.add/remove:
    # we compute requirement after the change, no matter reverse or not
    if signal_action in ["post_add", "post_remove"]:
        user_profile_qs = (
            UserProfile.objects.filter(user=instance)
            if not reverse
            else UserProfile.objects.filter(user_id__in=kwargs["pk_set"])
        )
        requires_2fa = Exists(
            Subquery(
                Group.objects.filter(user=OuterRef("user_id"), name__regex=group_regex)
            )
        )

    # group.users.clear: no user has this group any longer but they can be in other groups that require 2fa
    # so we recompute them all
    # We need to do that prior to the clear, otherwise the related user pool is lost
    if (
        signal_action == "pre_clear"
        and reverse
        and re.match(group_regex, instance.name)
    ):
        user_profile_qs = UserProfile.objects.filter(user__groups=instance)
        requires_2fa = Exists(
            Subquery(
                Group.objects.filter(
                    user=OuterRef("user_id"), name__regex=group_regex
                ).exclude(pk=instance.pk)
            )
        )

    has_totp = Exists(
        Subquery(Authenticator.objects.filter(type="totp", user_id=OuterRef("user_id")))
    )

    user_profile_qs.update(requires_2fa=requires_2fa)
    user_profile_qs.filter(requires_2fa=True).update(login_with_code=~has_totp)


@receiver(authenticator_added, sender=Authenticator)
def no_double_2fa(sender, request, user, authenticator, **kwargs):
    if user.profile.login_with_code:
        user.profile.login_with_code = False
        user.profile.save()


@receiver(authenticator_removed, sender=Authenticator)
def ensure_staff_2fa(sender, request, user, authenticator, **kwargs):
    if user.profile.requires_2fa and not user.profile.login_with_code:
        user.profile.login_with_code = True
        user.profile.save()


# eof
