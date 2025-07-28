# encoding: utf-8

"""
Utilities for recoco project

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-29 09:16:14 CEST
"""

import unicodedata
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from typing import AnyStr
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

from django.conf import settings
from django.contrib.auth import models as auth
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.db import migrations
from django.db import models as db_models
from django.db.models.functions import Cast
from django.http import HttpResponseBadRequest
from sesame.tokens import create_token


def make_site_slug(site: Site):
    return site.domain.translate(str.maketrans("-.", "__")).lower()


def make_group_name_for_site(name: str, site: Site) -> str:
    """Make a group label usable by django for the given site"""
    prefix = make_site_slug(site)
    return f"{prefix}_{name}"


def get_group_for_site(name: str, site: Site, create=False) -> auth.Group:
    """Return the Group with given name for site"""
    group_name = make_group_name_for_site(name, site)
    try:
        return auth.Group.objects.get(name=group_name)
    except auth.Group.DoesNotExist as exc:
        if not create:
            raise ImproperlyConfigured(
                f"Please create the required groups for site'{site}'"
            ) from exc

        return auth.Group.objects.create(name=group_name)


########################################################################
# View helpers
########################################################################


def has_perm(user, permission, obj=None):
    """
    Check if this user has the required permission for the given
    object on the current site.
    """
    return user.has_perm(permission, obj)


def has_perm_or_403(user, permission, obj=None):
    """Raise a 403 error is user does not have the given permission"""
    if not has_perm(user, permission, obj):
        raise PermissionDenied("L'information demandée n'est pas disponible")


def is_staff_for_site(user, site=None):
    if user.is_superuser:
        return True

    site = site or Site.objects.get_current()
    group_name = make_group_name_for_site("staff", site)
    return user.groups.filter(name=group_name).exists()


def is_admin_for_site(user, site=None):
    if user.is_superuser:
        return True

    site = site or Site.objects.get_current()
    group_name = make_group_name_for_site("admin", site)
    return user.groups.filter(name=group_name).exists()


def is_staff_for_site_or_403(user, site=None):
    """Raise a 403 error is user is not a staff member"""
    if not is_staff_for_site(user, site):
        raise PermissionDenied("L'information demandée n'est pas disponible")


def is_switchtender_or_403(user, site=None):
    """Raise a 403 error is user is not a switchtender"""
    if not user or not check_if_advisor(user, site):
        raise PermissionDenied("L'information demandée n'est pas disponible")


def check_if_advisor(user, site=None):
    """Return true if user is advisor for site. Defaults to current site."""
    if user.is_superuser:
        return True

    site = site or Site.objects.get_current()
    group_name = make_group_name_for_site("advisor", site)
    return auth.User.objects.filter(pk=user.id, groups__name=group_name).exists()


def build_absolute_url(path, auto_login_user=None, site=None):
    """
    Where we can't use request,
    use this to build the absolute url,
    assuming we're always using https
    """
    if site:
        current_site = site
    else:
        current_site = Site.objects.get_current()

    base = "https://" + current_site.domain
    url = urljoin(base, path)

    if auto_login_user:
        # Check if the account is sensitive and should not allow autologin
        sensitive_account = (
            auto_login_user.is_staff
            | auto_login_user.is_superuser
            | is_staff_for_site(auto_login_user)
            | is_admin_for_site(auto_login_user)
        )

        if not sensitive_account:
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)

            url = urlunparse(
                parsed_url._replace(
                    query=urlencode(
                        params
                        | {
                            getattr(settings, "SESAME_TOKEN_NAME", "sesame"): [
                                create_token(user=auto_login_user)
                            ]
                        },
                        doseq=True,
                    )
                )
            )

    return url


def assign_site_staff(site, user):
    """Make someone staff on this site"""
    staff_group = get_group_for_site("staff", site, create=True)
    user.profile.sites.add(site)
    staff_group.user_set.add(user)


def assign_site_admin(site, user):
    """Make someone admin on this site"""
    staff_group = get_group_for_site("admin", site, create=True)
    user.profile.sites.add(site)
    staff_group.user_set.add(user)


########################################################################
# Test helpers
########################################################################


@contextmanager
def login(
    client,
    is_staff=False,
    user=None,
    groups=None,
    username="test",
    email="test@example.com",
):
    """Create a user and sign her into the application"""
    groups = groups or []
    if not user:
        user = auth.User.objects.create_user(
            username=username, email=email, is_staff=is_staff
        )
    for name in groups:
        group = auth.Group.objects.get(name=name)
        group.user_set.add(user)
    client.force_login(user)
    yield user


#######################################################################
# Database Helpers
#######################################################################


class CastedGenericRelation(GenericRelation):
    def get_joining_columns(self, reverse_join=False):
        return ()

    def get_extra_restriction(self, alias, remote_alias):
        cond = super().get_extra_restriction(alias, remote_alias)
        from_field = self.model._meta.pk
        to_field = self.remote_field.model._meta.get_field(self.object_id_field_name)
        lookup = from_field.get_lookup("exact")(
            Cast(from_field.get_col(alias), output_field=db_models.TextField()),
            to_field.get_col(remote_alias),
        )
        cond.add(lookup, "AND")
        return cond


######################################################################
# Migration helpers
######################################################################


def _read_sql_file(path: Path) -> AnyStr:
    with open(path, "r") as sql_file:
        return sql_file.read()


class RunSQLFile(migrations.RunSQL):
    """from https://stackoverflow.com/a/75656369"""

    def __init__(
        self,
        sql_file_path: Path,
        reverse_sql=None,
        state_operations=None,
        hints=None,
        elidable=False,
    ):
        sql = _read_sql_file(sql_file_path)
        super().__init__(
            sql=sql,
            reverse_sql=reverse_sql,
            state_operations=state_operations,
            hints=hints,
            elidable=elidable,
        )


def strip_accents(input: str) -> str:
    normalized = unicodedata.normalize("NFD", input)
    return "".join([char for char in normalized if unicodedata.category(char) != "Mn"])


########
# HTMX #
########


def require_htmx(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.htmx:
            return HttpResponseBadRequest("This view is only accessible via htmx")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


# eof
