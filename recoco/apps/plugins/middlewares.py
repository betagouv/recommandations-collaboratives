#!/usr/bin/env python

from django.db import connection
from django.http import HttpRequest

from .resolvers import set_enabled_plugins


class TenantPluginSchemaMiddleware:
    """Extends the database search path based on the current tenant name.
    This allows using plugins contained for each tenant.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        if (
            hasattr(request, "site_config")
            and request.site_config
            and request.site_config.schema_name
        ):
            # Publish enabled plugins to thread-local for the URL resolver
            set_enabled_plugins(request.site_config.enabled_plugins or [])

            schema = request.site_config.schema_name
            with connection.cursor() as cursor:
                # XXX schema_name is a SlugField, so it should be safe from injection
                cursor.execute(f"SET search_path TO {schema}, public")
        else:
            set_enabled_plugins([])

        return self.get_response(request)
