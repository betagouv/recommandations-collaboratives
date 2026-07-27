"""
signals definitions for home

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-27 08:06:10 CEST
"""

import sentry_sdk
from actstream import action
from allauth.account.signals import user_signed_up as allauth_user_signed_up
from allauth.mfa.models import Authenticator
from allauth.mfa.signals import authenticator_added, authenticator_removed
from django.contrib.auth.models import Group, User, update_last_login
from django.contrib.auth.signals import user_logged_in
from django.contrib.sites.shortcuts import get_current_site
from django.db import connection
from django.db.models import Exists, OuterRef, Q, Subquery, Value
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver
from psycopg import sql

from recoco import verbs
from recoco.apps.home.models import SiteConfiguration, UserProfile
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


@receiver(post_save, sender=SiteConfiguration)
def create_tenant_schema(sender, instance, **kwargs):
    """Create a PGSql schema for plugins upon SiteConfiguration creation"""
    if instance.schema_name:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(
                    sql.Identifier(instance.schema_name)
                )
            )


@receiver(m2m_changed, sender=User.groups.through)
def ensure_2fa_requirement(sender, instance, **kwargs):
    signal_action = kwargs.get("action")
    user_profile_qs = UserProfile.objects.none()
    if signal_action in ["post_add", "post_remove"]:
        user_profile_qs = (
            UserProfile.objects.filter(user=instance)
            if not kwargs["reverse"]
            else UserProfile.objects.filter(user_id__in=kwargs["pk_set"])
        )
    if signal_action == "post_clear" and not kwargs["reverse"]:
        user_profile_qs = UserProfile.objects.filter(user=instance)

    requires_2fa = Exists(
        Subquery(
            Group.objects.filter(user=OuterRef("user_id")).filter(
                Q(name__contains="staff") | Q(name__contains="admin")
            )
        )
    )

    if (
        signal_action == "pre_clear"
        and kwargs["reverse"]
        and ("staff" in instance.name or "admin" in instance.name)
    ):
        user_profile_qs = UserProfile.objects.filter(user__groups=instance)
        requires_2fa = Value(False)

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
