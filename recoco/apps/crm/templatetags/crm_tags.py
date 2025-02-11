# encoding: utf-8

"""
Template tags for crm

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template

from recoco.apps.projects.models import Project

register = template.Library()


@register.simple_tag
def projects_for_tag(tag_name):
    """Return a list of projects tagged with the given tag"""
    return Project.on_site.filter(tags__name=tag_name).order_by("name")


@register.simple_tag
def note_update_url_name(related_ct: str) -> str | None:
    return {
        "organisation": "crm-organization-note-update",
        "utilisateur": "crm-user-note-update",
        "project": "crm-project-note-update",
    }.get(related_ct.lower(), None)
