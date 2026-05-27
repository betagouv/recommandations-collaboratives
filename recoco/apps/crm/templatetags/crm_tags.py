# encoding: utf-8

"""
Template tags for crm

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-29 11:30:42 CEST
"""

from django import template
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.urls import NoReverseMatch, reverse

from recoco.apps.addressbook.models import Organization
from recoco.apps.crm.models import Note
from recoco.apps.plugins.manager import get_tenant_hook
from recoco.apps.projects.models import Project

register = template.Library()


@register.simple_tag(takes_context=True)
def crm_plugin_tabs(context, min_index, max_index):
    """Return plugin-defined CRM navigation tabs whose index falls in (min_index, max_index)."""
    request = context.get("request")
    if request is None:
        return []
    tabs = []
    for tab in get_tenant_hook(request).hook.crm_navigation_tabs(request=request):
        if min_index < tab["index"] < max_index:
            try:
                tab = {**tab, "url": reverse(tab["url_name"])}
            except NoReverseMatch:
                continue
            tabs.append(tab)
    return sorted(tabs, key=lambda t: t["index"])


@register.simple_tag
def projects_for_tag(tag_name):
    """Return a list of projects tagged with the given tag"""
    return Project.on_site.filter(tags__name=tag_name).order_by("name")


@register.simple_tag
def get_note_update_url(note: Note) -> str | None:
    project_ct = ContentType.objects.get_for_model(Project)
    organization_ct = ContentType.objects.get_for_model(Organization)
    user_ct = ContentType.objects.get_for_model(User)

    match note.content_type.id:
        case project_ct.id:
            return reverse("crm-project-note-update", args=(note.object_id, note.id))
        case user_ct.id:
            return reverse("crm-user-note-update", args=(note.object_id, note.id))
        case organization_ct.id:
            return reverse(
                "crm-organization-note-update", args=(note.object_id, note.id)
            )
        case _:
            return None
