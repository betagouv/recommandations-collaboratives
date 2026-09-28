# encoding: utf-8

"""
Template tags for plugin

created: 2026-09-08 11:30:42 CEST
"""

from django import template
from django.urls import NoReverseMatch, reverse

from recoco.apps.plugins.manager import get_site_plugin_manager

register = template.Library()


@register.simple_tag(takes_context=True)
def plugin_tabs(context, hook_name, min_index, max_index):
    """Return plugin-defined navigation tabs to render between two builtin tabs.

    Plugins register tabs via the hook_name, each returning a
    dict with an ``index`` (see CrmSpec.crm_navigation_tabs for the full dict
    shape). This tag is called once between each pair of adjacent builtin tabs,
    with min_index and max_index set to their respective indexes, and returns
    only the plugin tabs whose index falls strictly in that (min_index, max_index)
    range, sorted by index. This lets a plugin position its tab anywhere in the
    navigation by picking an index between the two builtin tabs it should appear
    between (e.g. index=25 to insert between index 20 and 30).

    Tabs whose url_name cannot be reversed (e.g. the owning plugin is disabled
    on the current tenant) are silently dropped.

    Example template usage, inserting plugin tabs between 10 and 20:

        {% plugin_tabs "crm_navigation_tabs" 10 20 as plugin_tabs %}
        {% for tab in plugin_tabs %}
            ...
        {% endfor %}
    """

    request = context.get("request")
    if request is None:
        return []

    try:
        hook_caller = getattr(get_site_plugin_manager(request).hook, hook_name)
    except AttributeError as e:
        raise template.TemplateSyntaxError(
            f"{hook_name}: ce nom de hook n'existe pas "
        ) from e

    current_view_name = (
        request.resolver_match.view_name if request.resolver_match else ""
    )

    tabs = []
    for tab in hook_caller(request=request):
        if min_index < tab["index"] < max_index:
            try:
                tab = {
                    **tab,
                    "url": reverse(tab["url_name"]),
                    "active": current_view_name == tab["url_name"],
                }
            except NoReverseMatch:
                continue
            tabs.append(tab)
    return sorted(tabs, key=lambda t: t["index"])
