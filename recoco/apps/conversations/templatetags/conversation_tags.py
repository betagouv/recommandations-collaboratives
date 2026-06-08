from django import template
from django.utils.safestring import mark_safe

from recoco.apps.plugins.manager import get_tenant_hook

register = template.Library()


@register.simple_tag(takes_context=True)
def conversation_plugin_node_html(context, request, project):
    """Render Alpine x-if blocks for all plugin-defined node types."""
    hook = get_tenant_hook(request)
    results = hook.hook.conversation_message_node_html(request=request, project=project)
    return mark_safe("".join(r for r in results if r))  # noqa we are in control of the widget rendered, no user imput
