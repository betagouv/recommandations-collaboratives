#!/usr/bin/env python

from django.http import HttpRequest

from .context import tenant_plugins_context


class TenantPluginsMiddleware:
    """Enables the current tenant's plugins (hooks, URLs) for the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        site_config = getattr(request, "site_config", None)
        with tenant_plugins_context(site_config):
            return self.get_response(request)
