#!/usr/bin/env python
import importlib

from .manager import get_plugin_manager
from .resolvers import PluginURLResolver

urlpatterns = []

pm = get_plugin_manager()

# Fill urlpatterns with plugin patterns
for name, plugin in pm.list_name_plugin():
    urls_module = getattr(plugin, "urls_module", None)

    if urls_module is None:
        continue

    # Try to import the module, fail loudly if not found
    importlib.import_module(urls_module)

    urlpatterns.append(PluginURLResolver(name, "", urls_module))
