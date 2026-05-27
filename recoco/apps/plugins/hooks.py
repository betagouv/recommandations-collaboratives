#!/usr/bin/env python

import pluggy

hookspec = pluggy.HookspecMarker("recoco")


class ProjectSpec:
    @hookspec
    def project_tab_entries(self):
        """Return a list of of views with names to add."""


class ResourceSpec:
    @hookspec
    def resource_sidebar_panels(self, resource, request):
        """Return an HTML string to inject into the resource detail right sidebar."""


class CrmSpec:
    @hookspec
    def crm_project_list_annotations(self, request):
        """Return a dict of annotation kwargs to add to the CRM project list queryset.

        Example: {"realisations_count": Count("realisations")}
        """

    @hookspec
    def crm_project_list_extra_serializer_fields(self, request):
        """Return a list of field names (strings) to include in the project list
        REST response. Each name must match an annotation added via
        crm_project_list_annotations.

        Example: ["realisations_count"]
        """

    @hookspec
    def crm_project_list_columns(self, request):
        """Return a column definition dict for the CRM project list table.

        Keys:
          header (str)     — plain text for the <th>
          cell_html (str)  — raw HTML for the <td>, may contain Alpine.js expressions
                             (project is in scope, e.g. x-text="project.my_field")
          col_class (str)  — optional <col> CSS class (default: "col--medium")
        """
