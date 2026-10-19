from django.apps import apps

PLUGIN_APP_PREFIX = "plugin_"


def is_plugin_label(app_label):
    return app_label.startswith(PLUGIN_APP_PREFIX)


def get_plugin_app_labels():
    """Labels of the installed plugin apps, which are also their schema names."""
    return [
        app_config.label
        for app_config in apps.get_app_configs()
        if is_plugin_label(app_config.label)
    ]
