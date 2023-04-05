# encoding: utf-8

"""
Extra template tags for projects

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template

from .. import models

from urbanvitaliz import utils as uv_utils

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


# eof
