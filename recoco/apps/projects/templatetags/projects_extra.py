# encoding: utf-8

"""
Extra template tags for projects

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template
from django.contrib.sites.models import Site

from recoco import utils as uv_utils

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
    return uv_utils.is_staff_for_site(user)


@register.simple_tag
def is_admin_for_current_site(user):
    """Return True if the given user is admin for the active site"""
    return uv_utils.is_admin_for_site(user)


@register.simple_tag
def get_advising_position(user, project, site):
    """Return position of user for project on current site as dict

    {"is_observer": bool, "is_advisor": bool}
    """
    try:
        ps = models.ProjectSwitchtender.objects.get(
            switchtender=user, project=project, site=site
        )
        # obsevrer and advisor and in mutual exclusion
        return {"is_observer": ps.is_observer, "is_advisor": not ps.is_observer}
    except models.ProjectSwitchtender.DoesNotExist:
        return {"is_observer": False, "is_advisor": False}


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


# eof
