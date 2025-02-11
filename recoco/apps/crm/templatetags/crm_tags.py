# encoding: utf-8

"""
Template tags for crm

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template
from django.urls import reverse

from recoco.apps.crm.models import Note
from recoco.apps.projects.models import Project

register = template.Library()


@register.simple_tag
def projects_for_tag(tag_name):
    """Return a list of projects tagged with the given tag"""
    return Project.on_site.filter(tags__name=tag_name).order_by("name")


@register.simple_tag
def get_note_update_url(note: Note) -> str | None:
    match note.content_type.name.lower():
        case "project":
            return reverse("crm-project-note-update", args=(note.object_id, note.id))
        case "utilisateur":
            return reverse("crm-user-note-update", args=(note.object_id, note.id))
        case "organization":
            return reverse(
                "crm-organization-note-update", args=(note.object_id, note.id)
            )
        case _:
            return None
