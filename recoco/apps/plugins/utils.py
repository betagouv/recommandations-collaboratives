from django.apps import apps
from psycopg.sql import SQL, Identifier

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


def get_plugin_search_path():
    """public first, so core tables and public.django_migrations always win."""
    return ["public", *get_plugin_app_labels()]


def set_plugin_search_path(connection):
    """Put the plugin schemas on the connection's search_path."""
    with connection.cursor() as cursor:
        cursor.execute(
            SQL("SET search_path TO {}").format(
                SQL(", ").join(
                    Identifier(schema) for schema in get_plugin_search_path()
                )
            )
        )


def set_plugin_search_path_on_connection(sender, connection, **kwargs):
    """connection_created receiver: every new postgres connection (web,
    celery, commands, shell) starts with the plugin schemas on its search_path.
    """
    if connection.vendor == "postgresql":
        set_plugin_search_path(connection)
