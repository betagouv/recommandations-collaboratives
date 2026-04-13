Plugin System
#############

Recoco supports tenant-specific plugins: independent Python packages that add
UI, logic, and isolated database tables to a single portal without affecting
others.

.. contents:: Table of Contents
   :local:
   :depth: 2


Architecture Overview
=====================

.. code-block:: text

    ┌─────────────────────────────────────────────┐
    │               Recoco Core                   │
    │  (public schema, shared across all tenants) │
    └────────────────────┬────────────────────────┘
                         │ pluggy hooks
           ┌─────────────┴──────────────┐
           ▼                            ▼
    ┌─────────────┐             ┌─────────────┐
    │ plugin_lyon │             │plugin_giphy │
    │(tenant_lyon │             │(tenant_paris│
    │   schema)   │             │   schema)   │
    └─────────────┘             └─────────────┘

Three mechanisms work together:

- **pluggy** — defines a formal hook contract between the core and plugins.
- **PostgreSQL schemas** — each tenant gets an isolated schema for its plugin
  tables; the ``public`` schema holds shared core data.
- **PluginURLResolver** — routes are only exposed to the tenant that has the
  plugin enabled.


Plugin Package Structure
========================

A plugin is a standard Python package, typically named ``plugin_<name>``,
with an entry point that registers it with the core.

.. code-block:: text

    plugin_giphy/              ← package root (contains pyproject.toml)
    ├── pyproject.toml
    └── plugin_giphy/          ← Django app
        ├── __init__.py
        ├── apps.py
        ├── plugin.py          ← pluggy hook implementations
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── templates/
        │   └── plugin_giphy/
        │       └── search.html
        └── migrations/
            └── 0001_initial.py


``pyproject.toml``
------------------

The entry point under ``recoco.plugins`` is what the core uses to discover
the plugin automatically at startup.

.. code-block:: toml

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

    [project]
    name = "plugin-giphy"
    version = "0.1.0"
    requires-python = ">=3.11"
    dependencies = ["django>=4.2"]

    [project.entry-points."recoco.plugins"]
    plugin_giphy = "plugin_giphy.plugin:GiphyPlugin"

    [tool.hatch.build.targets.wheel]
    packages = ["plugin_giphy"]


``apps.py``
-----------

The ``AppConfig.name`` must match the top-level package name exactly so that
Django can resolve migrations and models correctly.

.. code-block:: python

    from django.apps import AppConfig

    class PluginGiphyConfig(AppConfig):
        default_auto_field = "django.db.models.BigAutoField"
        name = "plugin_giphy"


Defining a Hook Specification
==============================

Hook specifications live in ``recoco/apps/plugins/hooks.py``.  They declare
the *contract* — name, parameters, and return-value semantics — that every
plugin implementation must follow.

Each spec class is registered with the global plugin manager once in
``manager.py`` via ``pm.add_hookspecs()``.

The existing ``ProjectSpec`` class is the canonical home for project-related
hooks:

.. code-block:: python

    # recoco/apps/plugins/hooks.py
    import pluggy

    hookspec = pluggy.HookspecMarker("recoco")


    class ProjectSpec:
        @hookspec
        def project_tab_entries(self):
            """Return a list of (url_name, label) tuples to add as project tabs.

            Each plugin that implements this hook contributes one or more
            entries.  The core collects all results with::

                pm.hook.project_tab_entries()

            which returns a list of lists (one per registered plugin).
            """

Anatomy of a hookspec decorator
---------------------------------

``@hookspec`` supports several keyword arguments that change call semantics:

``firstresult=True``
    Stop calling further plugins as soon as one returns a non-``None`` value.
    Useful for hooks that should be *overridden* rather than *aggregated*
    (e.g. a single renderer or a permission gate).

``historic=True``
    Replay the hook call for late-registered plugins (plugins added after the
    hook was already called).  Useful during app initialisation.

``warn_on_impl``
    Emit a warning whenever a plugin implements this hook.  Handy for
    deprecating a hook without removing it.

Example — adding a new hookspec
---------------------------------

Suppose you want every enabled plugin to be able to inject extra context into
the project-detail view.  Add the spec to ``ProjectSpec``:

.. code-block:: python

    # recoco/apps/plugins/hooks.py
    class ProjectSpec:
        @hookspec
        def project_tab_entries(self):
            """Return a list of (url_name, label) tuples to add as project tabs."""

        @hookspec
        def project_detail_extra_context(self, request, project):
            """Return a dict of extra template context for the project-detail view.

            Each plugin returns a dict; the core merges all dicts together::

                extra = {}
                for ctx in pm.hook.project_detail_extra_context(
                    request=request, project=project
                ):
                    extra.update(ctx)
            """

Then call it in the core view:

.. code-block:: python

    # recoco/apps/projects/views.py
    from recoco.apps.plugins.manager import get_tenant_hook

    def project_detail(request, pk):
        project = get_object_or_404(Project, pk=pk)
        pm = get_tenant_hook(request)

        extra_context = {}
        for ctx in pm.hook.project_detail_extra_context(
            request=request, project=project
        ):
            extra_context.update(ctx)

        return render(request, "projects/detail.html", {
            "project": project,
            **extra_context,
        })

Hook Implementation (``plugin.py``)
------------------------------------

Plugins implement hooks defined by the core using ``pluggy``.

.. code-block:: python

    # plugin_giphy/plugin.py
    import pluggy

    hookimpl = pluggy.HookimplMarker("recoco")

    class GiphyPlugin:
        urls_module = "plugin_giphy.urls"

        @hookimpl
        def project_tab_entries(self):
            """Inject a "Giphy" tab on every project page."""
            return ("plugin_giphy:search", "Giphy")

        @hookimpl
        def project_detail_extra_context(self, request, project):
            """Add trending GIFs to the project-detail context."""
            return {"trending_gifs": ["https://example.com/1.gif"]}


Database Isolation
==================

Each plugin tenant gets its own PostgreSQL schema. Plugin models are
created there and can safely reference core models in the ``public`` schema
via foreign keys.

.. code-block:: python

    # plugin_giphy/models.py
    from django.db import models
    from recoco.apps.projects.models import Project

    class GiphySearch(models.Model):
        project = models.ForeignKey(Project, on_delete=models.CASCADE)
        query = models.CharField(max_length=255)

.. note::

   Plugin migrations must be run with the ``migrate_tenant`` command, not the
   standard ``migrate`` command. Running ``migrate`` against a ``plugin_*``
   app will raise an error.

.. code-block:: bash

    python manage.py migrate_tenant --schema=tenant_paris plugin_giphy


URL Routing
===========

Plugin routes are automatically discovered from the plugin manager and
wrapped in a ``PluginURLResolver`` that only exposes them to tenants with
the plugin enabled. No manual registration in the core ``urls.py`` is needed.

``urls.py`` (plugin side)
--------------------------

The plugin must declare ``app_name`` for namespacing.

.. code-block:: python

    # plugin_giphy/urls.py
    from django.urls import path
    from . import views

    app_name = "plugin_giphy"

    urlpatterns = [
        path("search/", views.search, name="search"),
    ]

Resulting URL
-------------

Routes are mounted automatically at the root.

.. code-block:: text

    /projects/23/giphy/search/   →  plugin_giphy:search


.. note::

   If a plugin is not listed in the tenant's ``enabled_plugins``, its routes
   return 404 and ``{% url "plugin_giphy:search" %}`` raises ``NoReverseMatch``.


Complete Example
================

Below is a minimal end-to-end walkthrough: a Giphy search view accessible
from a project dashboard.

1. View
-------

.. code-block:: python

    # plugin_giphy/views.py
    from django.shortcuts import render

    def search(request):
        query = request.GET.get("q", "")
        # In a real plugin this would call the Giphy API
        results = [{"title": query, "url": "https://example.com/giphy.gif"}] if query else []
        return render(request, "plugin_giphy/search.html", {"query": query, "results": results})

2. Template
-----------

Plugin templates live inside the plugin package and are picked up
automatically by Django's template loader (the plugin must be in
``INSTALLED_APPS``).

.. code-block:: html+django

    {# plugin_giphy/templates/plugin_giphy/search.html #}
    {% extends "base.html" %}

    {% block content %}
    <h2>Giphy Search</h2>

    <form method="get">
      <input type="text" name="q" value="{{ query }}" placeholder="Search...">
      <button type="submit">Search</button>
    </form>

    {% if results %}
      <ul>
        {% for gif in results %}
          <li><img src="{{ gif.url }}" alt="{{ gif.title }}"></li>
        {% endfor %}
      </ul>
    {% endif %}
    {% endblock %}

3. Link from a core template
-----------------------------

Use the namespaced URL. If the plugin is disabled for this tenant the tag
raises ``NoReverseMatch``, so guard it with a check on ``enabled_plugins``:

.. code-block:: html+django

    {% if "plugin_giphy" in request.site_config.enabled_plugins %}
      <a href="{% url 'plugin_giphy:search' %}">Search Giphy</a>
    {% endif %}


Activation
==========

Plugins are activated per tenant through the ``SiteConfiguration`` admin:

1. Install the plugin package into the environment::

    uv add ./plugins/plugin_giphy

2. Add ``plugin_giphy`` to ``INSTALLED_APPS`` in the relevant settings file.

3. Create the tenant schema and run plugin migrations::

    python manage.py migrate_tenant --schema=tenant_paris plugin_giphy

4. In the Django admin, edit the ``SiteConfiguration`` for the target site:

   - Set ``schema_name`` to ``tenant_paris``.
   - Add ``"plugin_giphy"`` to the ``enabled_plugins`` JSON list.

On the next request, the middleware switches the PostgreSQL ``search_path``
to ``tenant_paris, public`` and the ``PluginURLResolver`` exposes the plugin
routes exclusively to that tenant.
