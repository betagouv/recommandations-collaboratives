from django.apps import apps
from django.core import checks

from .models import PluginModel


def is_plugin_app(app_config):
    return app_config.label.startswith("plugin_")


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
        if not is_plugin_app(app_config):
            continue
        for model in app_config.get_models():
            errors.extend(check_plugin_model(model))
    return errors
