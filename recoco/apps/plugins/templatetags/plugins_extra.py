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
def main_menu_plugin_link(context):
    """Return plugin-defined navigation tabs to render in main menu."""

    request = context.get("request")
    if request is None:
        return []
    current_view_name = (
        request.resolver_match.view_name if request.resolver_match else ""
    )
    tabs = []
    for tab in get_site_plugin_manager(request).hook.header_menu_entries(
        request=request
    ):
        try:
            tab = {
                **tab,
                "url": reverse(tab["url_name"]),
                "active": current_view_name == tab["url_name"],
            }
        except NoReverseMatch:
            continue
        tabs.append(tab)
    return tabs
