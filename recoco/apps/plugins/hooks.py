#!/usr/bin/env python

import pluggy

hookspec = pluggy.HookspecMarker("recoco")


class HookSpec:
    """Base class for hook specification namespaces.

    Subclassing this registers the spec in `all_specs()`, so the plugin
    manager picks it up automatically without touching manager.py.
    """


def all_specs():
    """Return every declared hook spec namespace."""
    return HookSpec.__subclasses__()


class ProjectSpec(HookSpec):
    @hookspec
    def project_tab_entries(self):
        """Return a tab entry to add to the project detail page navigation.

        Return a dict with keys:
          url_name (str)          — Django URL name the tab links to, resolved
                                    with the project pk as its single argument
                                    (may include a namespace, e.g.
                                    "myplugin:project-detail")
          label (str)             — display text for the tab
          active_url_names (list) — optional list of fully-qualified view names
                                    (``namespace:name``) that mark the tab as
                                    active. The tab is active when the current
                                    request's view name is in this list.
                                    Defaults to ``[url_name]`` when omitted.

        Example:
            @hookimpl
            def project_tab_entries(self):
                return {
                    "url_name": "plugin_giphy:project-detail-giphy",
                    "label": "Giphyme!",
                    "active_url_names": [
                        "plugin_giphy:project-detail-giphy",
                        "plugin_giphy:giphy-detail",
                    ],
                }
        """


class ResourceSpec(HookSpec):
    @hookspec
    def resource_sidebar_panels(self, resource, request):
        """Return an HTML string to inject into the resource detail right sidebar.

        The returned string MUST be wrapped with ``mark_safe()``; the framework
        renders it without an additional ``|safe`` filter.

        Example:
            @hookimpl
            def resource_sidebar_panels(self, resource, request):
                return mark_safe(render_to_string(
                    "plugin_giphy/resource_sidebar_panel.html",
                    {"resource": resource},
                    request=request,
                ))
        """


class ConversationSpec(HookSpec):
    @hookspec
    def conversation_message_node_html(self, request, project):
        """Return an HTML string containing Alpine <template x-if> blocks for rendering
        custom node types inline in the conversation message feed.
        The 'node' Alpine variable is in scope (from the x-for loop over element.nodes).

        The returned string MUST be wrapped with ``mark_safe()``.

        Example:
            @hookimpl
            def conversation_message_node_html(self, request, project):
                return mark_safe(render_to_string(
                    "plugin_giphy/node_giphy.html", {}, request=request
                ))
        """

    @hookspec
    def conversation_extra_html(self, request, project):
        """Return an HTML string injected once into the conversation page (outside the
        message feed loop). Useful for page-level assets (e.g. <script> / vite_asset
        tags) and globally-mounted UI such as modals listening to window events.

        The returned string MUST be wrapped with ``mark_safe()``.

        Example:
            @hookimpl
            def conversation_extra_html(self, request, project):
                return mark_safe(render_to_string("plugin_giphy/conversation_extra.html"))
        """


class DigestSpec(HookSpec):
    @hookspec
    def send_digests_for_staff_users(self, site, user, dry_run):
        """Called once per staff user before the standard digest loop.

        Implementations should:

        - Query ``user.notifications(manager="on_site").unsent()`` filtered to
          the verbs they own.
        - Build and send their email.
        - Call ``notifications.mark_as_sent()`` to prevent double-delivery by
          the standard digest loop that runs afterwards.

        Return the count of notifications consumed (0 if nothing was sent).

        Example::

            @hookimpl
            def send_digests_for_staff_users(self, site, user, dry_run):
                from .digests import send_my_digest
                return send_my_digest(site, user, dry_run)
        """


class CrmSpec(HookSpec):
    @hookspec
    def crm_navigation_tabs(self, request):
        """Return a tab definition dict to inject into the CRM navigation.

        Keys:
          label (str)     — display text
          url_name (str)  — Django URL name (may include namespace, e.g. "myplugin:crm-foo")
          tab_key (str)   — context variable name that marks this tab as active
                            (e.g. "realisations" → pass realisations=True in the include)
          index (int)     — insertion order; builtin tabs use multiples of 10:
                            Accueil=0, Dossiers=10, Utilisateurs=20, Organisations=30,
                            Ressources=40, Paramètres=50

        Example:
            @hookimpl
            def crm_navigation_tabs(self, request):
                return {
                    "label": "Giphy",
                    "url_name": "plugin_giphy:crm-giphy",
                    "tab_key": "giphy",
                    "index": 25,
                }
        """

    @hookspec
    def crm_project_list_annotations(self, request):
        """Return a dict of annotation kwargs to add to the CRM project list queryset.

        Example:
            @hookimpl
            def crm_project_list_annotations(self, request):
                return {"realisations_count": Count("realisations")}
        """

    @hookspec
    def crm_project_list_extra_serializer_fields(self, request):
        """Return a list of field names (strings) to include in the project list
        REST response. Each name must match an annotation added via
        crm_project_list_annotations.

        Example:
            @hookimpl
            def crm_project_list_extra_serializer_fields(self, request):
                return ["realisations_count"]
        """

    @hookspec
    def crm_project_list_columns(self, request):
        """Return a column definition dict for the CRM project list table.

        Keys:
          header (str)     — plain text for the <th>
          cell_html (str)  — raw HTML for the <td>, may contain Alpine.js expressions
                             (project is in scope, e.g. x-text="project.my_field")
          col_class (str)  — optional <col> CSS class (default: "col--medium")

        Example:
            @hookimpl
            def crm_project_list_columns(self, request):
                return {
                    "header": "Réalisations",
                    "cell_html": '<td x-text="project.realisations_count"></td>',
                    "col_class": "col--small",
                }
        """
