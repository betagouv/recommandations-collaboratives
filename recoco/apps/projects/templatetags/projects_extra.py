# encoding: utf-8

"""
Extra template tags for projects

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

import json

from django import template
from django.contrib.sites.models import Site
from django.forms import model_to_dict

from recoco import utils as recoco_utils
from recoco.apps.home.models import AdvisorAccessRequest

from .. import models

register = template.Library()


@register.simple_tag
def current_project(session):
    """Return current project contained in session"""
    try:
        project_id = session.get("project_id")
        return models.Project.on_site.get(id=project_id)
    except Exception:  # pragma: nocover noqa
        return


@register.simple_tag
def is_staff_for_current_site(user):
    """Return True if the given user is staff for the active site"""
    return recoco_utils.is_staff_for_site(user)


@register.simple_tag
def is_admin_for_current_site(user):
    """Return True if the given user is admin for the active site"""
    return recoco_utils.is_admin_for_site(user)


@register.simple_tag
def get_projectsite_for_site(project, site):
    """Return the ProjectSite for the given site"""
    try:
        return project.project_sites.get(site=site)
    except models.ProjectSite.DoesNotExist:
        return None


@register.simple_tag
def get_project_moderation_count():
    """Return the number of projects to moderate for the current site"""
    return models.Project.on_site.filter(
        project_sites__status="DRAFT",
        project_sites__site=Site.objects.get_current(),
        deleted=None,
    ).count()


@register.simple_tag
def get_advisor_access_requests_count():
    """Return the number of advisor access requests to moderate for the current site"""
    return (
        AdvisorAccessRequest.objects.filter(site=Site.objects.get_current())
        .pending()
        .count()
    )


@register.simple_tag
def is_project_owner(project, user):
    """Return True if the given user is the owner of the given project"""
    return project.owner == user


@register.filter(name="to_json")
def to_json(value, fields=None):
    """Transforme un objet Python en JSON avec des champs spécifiques."""
    if fields:
        field_list = [field.strip() for field in fields.split(",")]
        data = model_to_dict(value, fields=field_list)
    else:
        data = model_to_dict(value)
    return json.dumps(data)


@register.simple_tag
def count_has_notifications(feed_items):
    """Count elements with notifications (new message)"""
    return len([item for item in feed_items if item.get("notifications")])


@register.simple_tag
def count_message_by_type(feed_items, *args):
    """Count message by type in feed"""
    return len([item for item in feed_items if item.get("type") in args])


# eof
