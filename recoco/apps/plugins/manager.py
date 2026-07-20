#!/usr/bin/env python

import importlib.metadata

import pluggy
import sentry_sdk

from recoco.apps.home.models import SiteConfiguration

from .hooks import all_specs

# Global manager holding ALL discovered plugins
_plugin_manager = None


def _new_plugin_manager():
    """Return a fresh PluginManager with all declared hook specs registered."""
    pm = pluggy.PluginManager("recoco")
    for spec in all_specs():
        pm.add_hookspecs(spec)
    return pm


def get_plugin_manager():
    """Return the global plugin manager, initializing it on first call."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = _build_plugin_manager()
    return _plugin_manager


def _build_plugin_manager():
    pm = _new_plugin_manager()

    for dist in importlib.metadata.distributions():
        for ep in dist.entry_points:
            if ep.group == "recoco.plugins":
                try:
                    plugin_cls = ep.load()
                    pm.register(plugin_cls(), name=ep.name)
                except ModuleNotFoundError as e:
                    # Don't crash the whole site if a registered plugin's module is missing
                    sentry_sdk.capture_exception(e)

    return pm


def get_site_plugin_manager(request=None, site=None):
    """
    Return a plugin manager scoped to the current tenant.
    The only enabled plugins come from the SiteConfiguration

    if request is not available, try to to lookup the SiteConfiguration
    from the Site. If neither is given, return a blank plugin manager.
    """
    pm = get_plugin_manager()

    recoco_pm = _new_plugin_manager()

    site_config = None

    if request:
        site_config = getattr(request, "site_config", None)
    elif site:
        try:
            site_config = SiteConfiguration.objects.get(site=site)
        except SiteConfiguration.DoesNotExist:
            return recoco_pm

    # Feed the scoped plugin manager with enabled plugins
    if site_config and site_config.enabled_plugins:
        enabled = set(request.site_config.enabled_plugins)

        for name, plugin in pm.list_name_plugin():
            if name in enabled:
                recoco_pm.register(plugin, name=name)

    return recoco_pm
