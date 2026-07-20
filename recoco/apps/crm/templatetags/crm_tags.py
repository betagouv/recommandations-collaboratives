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
    """Return plugin-defined CRM navigation tabs to render between two builtin tabs.

    Plugins register tabs via the ``crm_navigation_tabs`` hook, each returning a
    dict with an ``index`` (see CrmSpec.crm_navigation_tabs for the full dict
    shape). Builtin CRM tabs occupy indexes 0, 10, 20, 30, 40, 50 (Accueil,
    Dossiers, Utilisateurs, Organisations, Ressources, Paramètres). This tag is
    called once between each pair of adjacent builtin tabs, with min_index and
    max_index set to their respective indexes, and returns only the plugin tabs
    whose index falls strictly in that (min_index, max_index) range, sorted by
    index. This lets a plugin position its tab anywhere in the navigation by
    picking an index between the two builtin tabs it should appear between
    (e.g. index=25 to insert between Utilisateurs and Organisations).

    Tabs whose url_name cannot be reversed (e.g. the owning plugin is disabled
    on the current tenant) are silently dropped.

    Example template usage, inserting plugin tabs between Dossiers (10) and
    Utilisateurs (20):

        {% crm_plugin_tabs 10 20 as plugin_tabs %}
        {% for tab in plugin_tabs %}
            ...
        {% endfor %}
    """
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


@register.simple_tag(takes_context=True)
def project_other_site_config(context, project):
    """return the configuration of the project on another site if it is not on the current site, else return None"""
    current_site_id = context["request"].site.id
    if project.is_on_site(current_site_id):
        return None

    project_sites = list(project.project_sites.all())
    origin = next(
        (ps for ps in project_sites if ps.is_origin),
        project_sites[0] if project_sites else None,
    )
    return getattr(origin.site, "configuration", None) if origin else None


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
