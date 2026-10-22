from django.apps import apps
from django.core import checks

from .manager import get_plugin_manager
from .models import PluginModel
from .utils import is_plugin_label


def check_plugin_model(model):
    """Return the errors for a single model of a plugin app."""
    opts = model._meta

    if opts.abstract or opts.proxy or not opts.managed or opts.auto_created:
        return []

    # Multi-table inheritance: the pk comes from the parent table, which is
    # checked on its own (or is a core model, scoped by core).
    if opts.parents:
        return []

    if issubclass(model, PluginModel):
        return []

    return [
        checks.Error(
            f"Plugin model {opts.label} must subclass PluginModel.",
            hint=(
                "Plugin tables are shared by all tenants, rows must be scoped "
                "by site: inherit from recoco.apps.plugins.models.PluginModel."
            ),
            obj=model,
            id="plugins.E001",
        )
    ]


@checks.register(checks.Tags.models)
def check_plugin_models(app_configs=None, **kwargs):
    if app_configs is None:
        app_configs = apps.get_app_configs()

    errors = []
    for app_config in app_configs:
        if not is_plugin_label(app_config.label):
            continue
        for model in app_config.get_models():
            errors.extend(check_plugin_model(model))
    return errors


def check_plugin_name(plugin_name, app_configs):
    """Return the errors for a registered plugin.

    A plugin is enabled by name (SiteConfiguration.enabled_plugins, hooks,
    urls) but its tables, search and objects are found by app label: both must
    be the same, prefixed ``plugin_`` so its tables go to its own schema.
    """
    if not is_plugin_label(plugin_name):
        return [
            checks.Error(
                f"Plugin {plugin_name} must be named plugin_<name>.",
                hint=(
                    "Name the plugin's entry point and app plugin_<name>, "
                    "otherwise its tables go to the public schema and it is "
                    "handled as a core app."
                ),
                obj=plugin_name,
                id="plugins.E002",
            )
        ]

    app_config = next((c for c in app_configs if c.name == plugin_name), None)
    if app_config is not None and app_config.label != plugin_name:
        return [
            checks.Error(
                f"Plugin {plugin_name} has app label {app_config.label}.",
                hint=(
                    "The plugin name and its app label must match: remove "
                    "the custom label from the plugin's AppConfig."
                ),
                obj=plugin_name,
                id="plugins.E003",
            )
        ]

    return []


@checks.register()
def check_plugin_names(app_configs=None, **kwargs):
    all_app_configs = list(apps.get_app_configs())
    errors = []
    for plugin_name, _ in get_plugin_manager().list_name_plugin():
        errors.extend(check_plugin_name(plugin_name, all_app_configs))
    return errors
