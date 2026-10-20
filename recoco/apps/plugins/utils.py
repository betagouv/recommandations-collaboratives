from django.apps import apps
from psycopg.sql import SQL, Identifier

from .resolvers import get_enabled_plugins

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


def get_disabled_plugin_app_labels():
    """Installed plugin apps that the current tenant has not enabled."""
    enabled_plugins = get_enabled_plugins()
    return [label for label in get_plugin_app_labels() if label not in enabled_plugins]


def is_disabled_plugin_model(model):
    """True if model belongs to a plugin the current tenant has not enabled."""
    return model._meta.app_label in get_disabled_plugin_app_labels()


def exclude_disabled_plugin_objects(queryset, *content_type_fields):
    """Drop rows whose content type fields (generic relations, polymorphic
    ctype) point to a model of a plugin the current tenant has not enabled.

    Plugin objects end up in core tables shared by every tenant (actstream
    actions, notifications, conversation nodes): they must not show up, nor
    be rendered (their urls don't reverse), where the plugin is disabled.
    """
    from django.contrib.contenttypes.models import ContentType

    labels = get_disabled_plugin_app_labels()
    if not labels:
        return queryset

    plugin_models = [
        model for label in labels for model in apps.get_app_config(label).get_models()
    ]
    content_type_ids = [
        ct.id for ct in ContentType.objects.get_for_models(*plugin_models).values()
    ]
    for field in content_type_fields:
        queryset = queryset.exclude(**{f"{field}__in": content_type_ids})
    return queryset
