#!/usr/bin/env python

import pluggy

hookspec = pluggy.HookspecMarker("recoco")


class ProjectSpec:
    @hookspec
    def project_tab_entries(self):
        """Return a list of of views with names to add."""
