# encoding: utf-8

"""
Template tags for crm

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template
from urbanvitaliz.apps.projects.models import Project

register = template.Library()


@register.simple_tag
def projects_for_tag(tag_name):
    """Return a list of projects tagged with the given tag"""
    return Project.on_site.filter(tags__name=tag_name).order_by("name")
