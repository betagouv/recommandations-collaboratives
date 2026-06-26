from django import template
from django.utils.html import format_html

from recoco.apps.plugins.manager import get_tenant_hook

register = template.Library()


@register.simple_tag(takes_context=True)
def conversation_plugin_node_html(context, request, project):
    """Render Alpine x-if blocks for all plugin-defined node types."""
    hook = get_tenant_hook(request)
    results = [
        r
        for r in hook.hook.conversation_message_node_html(
            request=request, project=project
        )
        if r
    ]
    return format_html("".join("{}" for _ in results), *results)


@register.simple_tag(takes_context=True)
def conversation_plugin_extra_html(context, request, project):
    """Render plugin-defined HTML injected once into the conversation page."""
    hook = get_tenant_hook(request)
    results = [
        r
        for r in hook.hook.conversation_extra_html(request=request, project=project)
        if r
    ]
    return format_html("".join("{}" for _ in results), *results)
