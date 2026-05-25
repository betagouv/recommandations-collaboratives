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
