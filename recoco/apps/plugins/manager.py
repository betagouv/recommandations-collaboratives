#!/usr/bin/env python

import importlib.metadata

import pluggy

from .hooks import ProjectSpec

# Global manager holding ALL discovered plugins
_plugin_manager = None


def get_plugin_manager():
    """Return the global plugin manager, initializing it on first call."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = _build_plugin_manager()
    return _plugin_manager


def _build_plugin_manager():
    pm = pluggy.PluginManager("recoco")
    pm.add_hookspecs(ProjectSpec)

    for dist in importlib.metadata.distributions():
        for ep in dist.entry_points:
            if ep.group == "recoco.plugins":
                try:
                    plugin_cls = ep.load()
                    pm.register(plugin_cls(), name=ep.name)
                except ModuleNotFoundError:
                    pass  # Fail silently if the module is not found to prevent a global crash

    return pm


def get_tenant_hook(request):
    """
    Return a plugin manager scoped to the current tenant.
    The only enabled plugins come from the SiteConfiguration
    """
    pm = get_plugin_manager()

    recoco_pm = pluggy.PluginManager("recoco")
    recoco_pm.add_hookspecs(ProjectSpec)

    # Feed the scoped plugin manager with enabled plugins
    enabled = set(request.site_config.enabled_plugins)

    for name, plugin in pm.list_name_plugin():
        if name in enabled:
            recoco_pm.register(plugin, name=name)

    return recoco_pm
