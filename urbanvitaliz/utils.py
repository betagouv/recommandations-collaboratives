# encoding: utf-8

"""
Utilities for urbanvitaliz project

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-29 09:16:14 CEST
"""

from contextlib import contextmanager
from urllib.parse import urljoin

from django.conf import settings
from django.contrib.auth import models as auth
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.core.mail import send_mail
from django.db import models as db_models
from django.db.models.functions import Cast
from django.template import loader
from sesame.utils import get_query_string

from urbanvitaliz.apps.home.models import SiteConfiguration

########################################################################
# View helpers
########################################################################


def is_staff_or_403(user):
    """Raise a 403 error is user is not a staff member"""
    if not user or not user.is_staff:
        raise PermissionDenied("L'information demandée n'est pas disponible")


def is_switchtender_or_403(user):
    """Raise a 403 error is user is not a switchtender"""
    if not user or not check_if_switchtender(user):
        raise PermissionDenied("L'information demandée n'est pas disponible")


def check_if_switchtender(user):
    """Return true if user is a global switchtender"""
    return auth.User.objects.filter(pk=user.id, groups__name="switchtender").exists()


def send_email(
    request, user_email, email_subject, template_base_name, extra_context=None
):
    """Send an email raw or html, inspired by magicauth"""
    html_template = template_base_name + ".html"
    text_template = template_base_name + ".txt"
    from_email = settings.EMAIL_FROM

    context = {"site": get_current_site(request), "request": request}
    if extra_context:
        context.update(extra_context)

    text_message = loader.render_to_string(text_template, context)
    html_message = loader.render_to_string(html_template, context)

    send_mail(
        subject=email_subject,
        message=text_message,
        from_email=from_email,
        html_message=html_message,
        recipient_list=[user_email],
        fail_silently=False,
    )


def build_absolute_url(path, auto_login_user=None):
    """
    Where we can't use request,
    use this to build the absolute url,
    assuming we're always using https
    """
    current_site = Site.objects.get_current()
    base = "https://" + current_site.domain
    url = urljoin(base, path)

    if auto_login_user:
        url = urljoin(url, get_query_string(auto_login_user))

    return url


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


################################################################
# Site configuration
################################################################
def get_site_config_or_503(site):
    try:
        return SiteConfiguration.objects.get(site=site)
    except SiteConfiguration.DoesNotExist:
        raise ImproperlyConfigured(
            f"Please create a SiteConfiguration for '{site}' before using this feature.",
        )


#######################################################################
# Database Helpers
#######################################################################
class CastedGenericRelation(GenericRelation):
    def get_joining_columns(self, reverse_join=False):
        return ()

    def get_extra_restriction(self, where_class, alias, remote_alias):
        cond = super().get_extra_restriction(where_class, alias, remote_alias)
        from_field = self.model._meta.pk
        to_field = self.remote_field.model._meta.get_field(self.object_id_field_name)
        lookup = from_field.get_lookup("exact")(
            Cast(from_field.get_col(alias), output_field=db_models.TextField()),
            to_field.get_col(remote_alias),
        )
        cond.add(lookup, "AND")
        return cond


# eof
