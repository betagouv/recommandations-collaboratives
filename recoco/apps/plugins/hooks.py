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

        Return a 2-tuple ``(url_name, label)``:
          url_name (str) — Django URL name, resolved with the project pk as
                            its single argument (may include namespace, e.g.
                            "myplugin:project-detail")
          label (str)    — display text for the tab

        Example:
            @hookimpl
            def project_tab_entries(self):
                return ("plugin_giphy:project-detail-giphy", "Giphyme!")
        """


class ResourceSpec(HookSpec):
    @hookspec
    def resource_sidebar_panels(self, resource, request):
        """Return an HTML string to inject into the resource detail right sidebar.

        Example:
            @hookimpl
            def resource_sidebar_panels(self, resource, request):
                return render_to_string(
                    "plugin_giphy/resource_sidebar_panel.html",
                    {"resource": resource},
                    request=request,
                )
        """


class ConversationSpec(HookSpec):
    @hookspec
    def conversation_message_node_html(self, request, project):
        """Return an HTML string containing Alpine <template x-if> blocks for rendering
        custom node types inline in the conversation message feed.
        The 'node' Alpine variable is in scope (from the x-for loop over element.nodes).

        Example:
            @hookimpl
            def conversation_message_node_html(self, request, project):
                return '''
                <template x-if="node.type == 'giphy'">
                    <img :src="node.data.url" class="fr-responsive-img" />
                </template>
                '''
        """

    @hookspec
    def conversation_extra_html(self, request, project):
        """Return an HTML string injected once into the conversation page (outside the
        message feed loop). Useful for page-level assets (e.g. <script> / vite_asset
        tags) and globally-mounted UI such as modals listening to window events.

        Example:
            @hookimpl
            def conversation_extra_html(self, request, project):
                return render_to_string("plugin_giphy/conversation_extra.html")
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
