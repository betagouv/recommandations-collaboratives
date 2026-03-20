#!/usr/bin/env python

import pluggy

hookspec = pluggy.HookspecMarker("recoco")


class ProjectSpec:
    @hookspec
    def get_tab_views(self):
        """Return a list of of views with names to add."""
