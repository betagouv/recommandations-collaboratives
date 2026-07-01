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

- **pluggy** - defines a formal hook contract between the core and plugins.
- **PostgreSQL schemas** - each tenant gets an isolated schema for its plugin
  tables; the ``public`` schema holds shared core data.
- **PluginURLResolver** - routes are only exposed to the tenant that has the
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
the *contract* - name, parameters, and return-value semantics - that every
plugin implementation must follow.

Each spec class is registered with the global plugin manager once in
``manager.py`` via ``pm.add_hookspecs()``.

Hook spec classes are organized by domain. ``ProjectSpec`` is the canonical
home for project-related hooks; ``ResourceSpec`` for resource-related hooks:

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


    class ResourceSpec:
        @hookspec
        def resource_sidebar_panels(self, resource, request):
            """Return an HTML string to inject into the resource detail right sidebar.

            Each plugin renders its own fragment and returns the HTML string.
            The core collects all results and renders them in order::

                pm.hook.resource_sidebar_panels(resource=resource, request=request)

            which returns a list of HTML strings (one per registered plugin).
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

Example - adding a new hookspec
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


Available Hooks
================

The core ships with several hook specification namespaces, defined in
``recoco/apps/plugins/hooks.py``. Each ``@hookspec``-decorated method has a
full docstring with its return contract and an example - the list below is
a quick index.

``ProjectSpec``
---------------

``project_tab_entries()``
    Add a tab to the project detail page navigation. Returns
    ``(url_name, label)``.

``ResourceSpec``
----------------

``resource_sidebar_panels(resource, request)``
    Inject an HTML fragment into the resource detail right sidebar.

``ConversationSpec``
---------------------

``conversation_message_node_html(request, project)``
    Return Alpine ``<template x-if="node.type == '...'">`` fragments
    handling custom message node types in the conversation feed.

``conversation_extra_html(request, project)``
    Return HTML injected once into the conversation page - page-level
    assets (``<script>`` / ``{% vite_asset %}``) and globally-mounted UI
    such as modals.

See `Conversation Hooks & JS Integration`_ below for a worked example.

``CrmSpec``
-----------

``crm_navigation_tabs(request)``
    Add a tab to the CRM navigation. Returns a dict with ``label``,
    ``url_name``, ``tab_key`` and ``index``.

``crm_project_list_annotations(request)``
    Add queryset annotations (e.g. ``Count(...)``) to the CRM project list,
    avoiding N+1 queries.

``crm_project_list_extra_serializer_fields(request)``
    Expose annotated fields (declared via ``crm_project_list_annotations``)
    in the REST list response.

``crm_project_list_columns(request)``
    Add a column to the CRM project list table. Returns a dict with
    ``header``, ``cell_html`` and an optional ``col_class``.

See `CRM Project List Extension Example`_ below for how the three
``crm_project_list_*`` hooks work together.


CRM Project List Extension Example
====================================

The three ``crm_project_list_*`` hooks work together to add a column to the
CRM project list without N+1 queries:

.. code-block:: python

    # plugin_giphy/plugin.py
    from django.db.models import Count

    class GiphyPlugin:
        ...

        @hookimpl
        def crm_project_list_annotations(self, request):
            """Annotate the queryset so the count is computed in SQL."""
            return {"giphy_searches_count": Count("giphysearch")}

        @hookimpl
        def crm_project_list_extra_serializer_fields(self, request):
            """Expose the annotation in the REST payload."""
            return ["giphy_searches_count"]

        @hookimpl
        def crm_project_list_columns(self, request):
            """Render the column header and cell."""
            return {
                "header": "Recherches Giphy",
                "cell_html": '<td x-text="project.giphy_searches_count"></td>',
                "col_class": "col--small",
            }

- ``crm_project_list_annotations`` adds the queryset annotation.
- ``crm_project_list_extra_serializer_fields`` exposes it in the REST
  payload consumed by the Alpine table.
- ``crm_project_list_columns`` renders the ``<th>``/``<td>`` pair;
  ``project`` is in scope for ``cell_html`` Alpine expressions
  (``x-text``, ``:href``, etc.).


Conversation Hooks & JS Integration
====================================

The conversation feed (project detail → "Échanges") can be extended with
custom message node types - for example, a plugin that lets users share a
GIF inline in the discussion.

Two hooks work together on the Python side:

``conversation_message_node_html(request, project)``
    Returns an Alpine ``<template x-if="node.type == '...'">`` fragment. It
    is rendered inside the ``x-for="node in element.nodes"`` loop of every
    message, so the ``node`` variable is in scope.

``conversation_extra_html(request, project)``
    Returns HTML rendered once, outside the message loop. Use it to load the
    plugin's JS bundle (``{% vite_asset %}``) and to mount any page-level UI
    (e.g. a modal) that the JS below opens on demand.

Python side
-----------

.. code-block:: python

    # plugin_giphy/plugin.py
    from django.template.loader import render_to_string

    class GiphyPlugin:
        ...

        @hookimpl
        def conversation_message_node_html(self, request, project):
            return '''
            <template x-if="node.type == 'GiphyNode'">
                <img :src="node.data.url" class="fr-responsive-img" />
            </template>
            '''

        @hookimpl
        def conversation_extra_html(self, request, project):
            return render_to_string("plugin_giphy/conversation_extra.html")

.. code-block:: html+django

    {# plugin_giphy/templates/plugin_giphy/conversation_extra.html #}
    {% load django_vite %}
    {% vite_asset 'js/plugins/giphyConversation.js' %}

    <dialog id="giphy-modal" class="fr-modal" x-data="GiphyModal">
      <!-- ... GIF picker markup ... -->
    </dialog>

JS side: window events
-----------------------

The conversation feed communicates with plugin JS exclusively through
``window`` ``CustomEvent``\ s - plugin bundles never need direct access to
the ``Conversations`` Alpine component.

``task:done`` *(dispatched by the core)*
    Fired when a user marks a task as done from the conversation feed.

    .. code-block:: javascript

        window.dispatchEvent(new CustomEvent('task:done', {
          detail: { task, projectId, resourceId },
        }));

    A plugin can listen for this to offer a follow-up action - e.g. "share
    a celebratory GIF for this task".

``plugin-message-create-request`` *(dispatched by a plugin)*
    Ask the core to post a new conversation message containing
    plugin-defined nodes. The core POSTs the ``nodes`` to the conversation's
    messages endpoint and appends the result to the feed.

    .. code-block:: javascript

        window.dispatchEvent(new CustomEvent('plugin-message-create-request', {
          detail: { nodes: [{ type: 'GiphyNode', data: { url: gifUrl } }] },
        }));

``plugin-message-created`` *(dispatched by the core)*
    Fired after a ``plugin-message-create-request`` succeeds. Use it to
    close the plugin's modal or reset its state.

Putting it together
--------------------

.. code-block:: javascript

    // plugin_giphy/js/giphyConversation.js
    import Alpine from 'alpinejs';

    Alpine.data('GiphyModal', () => ({
      open: false,

      init() {
        window.addEventListener('task:done', () => {
          this.open = true;
        });
        window.addEventListener('plugin-message-created', () => {
          this.open = false;
        });
      },

      selectGif(gifUrl) {
        window.dispatchEvent(new CustomEvent('plugin-message-create-request', {
          detail: { nodes: [{ type: 'GiphyNode', data: { url: gifUrl } }] },
        }));
      },
    }));


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


Migration Mechanics
===================

Understanding how migrations are split between the public schema and tenant
schemas is essential for anyone working on the plugin system or debugging
migration issues.

The contract
------------

There are two categories of migration:

- **Core migrations** : all apps whose ``app_label`` does *not* start with
  ``plugin_``.  These belong to the ``public`` schema and are applied by the
  standard ``manage.py migrate`` command.
- **Plugin migrations** : apps whose ``app_label`` starts with ``plugin_``.
  These belong exclusively to the tenant schema for which the plugin is
  enabled.

The contract is enforced by ``TenantPluginRouter`` in
``recoco/apps/plugins/routers.py``:

.. code-block:: python

    class TenantPluginRouter:
        is_tenant_operation = False   # class-level flag, set by migrate_tenant

        def allow_migrate(self, db, app_label, model_name=None, **hints):
            if app_label.startswith("plugin_"):
                return self.is_tenant_operation   # only allowed in tenant mode
            return not self.is_tenant_operation   # core only allowed in normal mode

When ``is_tenant_operation`` is ``False`` (the default, i.e. a normal
``migrate`` run):

- Core migrations → **allowed** ✓
- Plugin migrations → **blocked** ✗

When ``is_tenant_operation`` is ``True`` (set by ``migrate_tenant``):

- Core migrations → **blocked** ✗
- Plugin migrations → **allowed** ✓

How ``allow_migrate`` is enforced (per operation, not per migration)
--------------------------------------------------------------------

A critical implementation detail: Django's migration *executor* does **not**
call ``allow_migrate`` before applying an individual migration.  It is called
instead by each **operation** inside the migration : ``CreateModel``,
``AddField``, ``RunSQL``, ``RunPython``, etc. immediately before executing
any SQL.  If ``allow_migrate`` returns ``False`` the operation is silently
skipped but the migration **is still recorded** in ``django_migrations``.

This means that even if a core migration ends up in the tenant's execution
plan (because it is a declared dependency of a plugin migration), its SQL
will never touch the tenant schema. The tables of core models live in
``public`` and are visible to the tenant via ``search_path`` : no copy is
created per tenant.


The ``django_migrations`` ghost-entry mechanism
-----------------------------------------------

Django's migration planner reads ``django_migrations`` to decide which
migrations still need to run.  Without intervention, an empty tenant
``django_migrations`` table would cause Django to include every core migration
in the plan. Not to execute them (the per-operation guard prevents that) but
to process them as no-ops, recording them one by one.  On a project with
hundreds of migrations this produces hundreds of ``Applying auth.0001...``
lines and a slow first run.

``migrate_tenant`` solves this with a single INSERT before running any plugin
migration:

.. code-block:: sql

    INSERT INTO "<schema>".django_migrations (app, name, applied)
    SELECT app, name, applied
    FROM public.django_migrations
    WHERE app NOT LIKE 'plugin_%'
      AND NOT EXISTS (
        SELECT 1 FROM "<schema>".django_migrations existing
        WHERE existing.app = public.django_migrations.app
          AND existing.name = public.django_migrations.name
      )

These are called **ghost entries**: records copied from the public schema that
tell Django "this core migration has already been accounted for : do not
include it in the tenant plan."

Why ghost entries are INSERT-only (no DELETE on rollback)
---------------------------------------------------------

A ghost entry for a core migration means *"do not re-apply this here"*.  That
statement remains true even if the core migration is later rolled back in
``public``.  The tenant never ran that migration's SQL; rolling it back in
``public`` changes the shared schema (which the tenant sees through
``search_path``), but it does not create any obligation for the tenant's
``django_migrations`` bookkeeping.

Deleting ghost entries on rollback would introduce a spurious inconsistency:
``django_migrations`` would show a plugin migration as applied while its core
dependency ghost was gone, causing ``check_consistent_history`` to raise
``InconsistentMigrationHistory`` on the next run.

Keeping stale ghosts avoids this problem and is semantically correct: the
ghost just continues to say "don't try to run this core migration in the
tenant", which is the right answer before and after any public rollback.

``migrate_tenant`` execution flow
----------------------------------

Putting it all together, here is what happens when you run:

.. code-block:: bash

    python manage.py migrate_tenant --schema=tenant_paris plugin_giphy

1. **Validation** : ``SiteConfiguration`` with ``schema_name="tenant_paris"``
   must exist; the PostgreSQL schema must be present (created by the
   ``post_save`` signal on ``SiteConfiguration``).

2. **Router flag** : ``TenantPluginRouter.is_tenant_operation = True``.
   From this point on ``allow_migrate`` blocks core migrations and permits
   plugin migrations.

3. **Create** ``django_migrations`` **in tenant** : ``search_path`` is
   temporarily set to *only* the tenant schema so that
   ``MigrationRecorder.ensure_schema()`` creates the table there rather than
   picking up ``public.django_migrations``.

4. **Ghost entry sync** : the INSERT above copies all unapplied core migration
   records from ``public.django_migrations`` into the tenant table.  Any core
   migration already present (from a previous run) is left untouched.

5. **Run plugin migrations** : ``search_path`` is restored to
   ``tenant_paris, public`` and ``call_command("migrate", "plugin_giphy")``
   is called.  Django sees all core migrations as applied (from the ghost
   entries) and only executes the plugin's own unapplied migrations.  Tables
   created by plugin migrations land in ``tenant_paris``; ForeignKeys to core
   models resolve through ``public`` via ``search_path``.

6. **Cleanup** : ``is_tenant_operation`` is reset to ``False`` and
   ``search_path`` is reset to ``public`` in a ``finally`` block.


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


REST API
========

Plugins can expose their own DRF API endpoints under the core ``/api/`` prefix
without touching ``recoco/rest_api/urls.py``.

Declare a ``rest_urls_module`` attribute on the plugin class pointing to a
module that contains a standard ``urlpatterns`` list:

.. code-block:: python

    # plugin_giphy/plugin.py
    class GiphyPlugin:
        urls_module = "plugin_giphy.urls"
        rest_urls_module = "plugin_giphy.rest_urls"   # ← new

.. code-block:: python

    # plugin_giphy/rest_urls.py
    from django.urls import path
    from .rest_api import GiphySearchAPIView

    urlpatterns = [
        path("giphy/search/", GiphySearchAPIView.as_view(), name="plugin-giphy-search"),
    ]

The core's ``recoco/rest_api/urls.py`` discovers all installed plugins that
carry ``rest_urls_module`` at import time and appends their patterns to the
global ``urlpatterns``.  The resulting endpoint is served under ``/api/``:

.. code-block:: text

    /api/giphy/search/   →  GiphySearchAPIView


Frontend (Vite / Alpine)
========================

Plugins can ship their own JavaScript - including npm dependencies - without
modifying the core frontend's ``package.json`` or ``vite.config.js``.

Plugin package layout
---------------------

Add a ``package.json`` at the plugin repo root.  The ``recocoPlugin.viteEntries``
field maps Vite entry names to JS file paths relative to the **plugin package
directory**:

.. code-block:: json

    {
      "name": "plugin-giphy",
      "private": true,
      "recocoPlugin": {
        "viteEntries": {
          "giphySearch": "js/giphySearch.js"
        }
      },
      "dependencies": {
        "some-npm-lib": "^1.0.0"
      }
    }

Install the plugin's own npm deps once:

.. code-block:: bash

    cd /path/to/plugin-giphy
    npm install

Writing the Alpine controller
-----------------------------

Place the entry file at the path declared in ``viteEntries``.  Register Alpine
data objects with ``Alpine.data()``:

.. code-block:: javascript

    // plugin_giphy/js/giphySearch.js
    import Alpine from 'alpinejs';
    import htmx from 'htmx.org';

    window.htmx = htmx;   // make htmx available to HTMX-powered templates

    function GiphySearch() {
      return {
        query: '',
        results: [],
        async search() { /* ... */ },
      };
    }

    Alpine.data('GiphySearch', GiphySearch);

The plugin entry can import packages from its own ``node_modules/`` (Node's
module resolution walks up the directory tree and finds them there) as well
as packages from the core frontend's ``node_modules/`` (Alpine, Leaflet,
lodash, etc.).

Importing core JS modules (``@core`` alias)
---------------------------------------------

The core ``vite.config.js`` defines an ``@core`` alias pointing at
``recoco/frontend/src/``. Plugin entry files can import core utilities,
stores, and components directly instead of duplicating them:

.. code-block:: javascript

    // plugin_giphy/js/giphyConversation.js
    import { STATUSES, isStatus } from '@core/utils/taskStatus';

This keeps plugin code in sync with core behaviour (e.g. task status enums)
without adding a dependency between npm packages.

Generating Vite entry proxies
------------------------------

Before building or starting the Vite dev server, run:

.. code-block:: bash

    python manage.py collect_plugin_vite_entries

This command:

1. Discovers all installed plugins that declare ``vite_entries`` on their
   plugin class (matching the keys in ``package.json`` ``recocoPlugin.viteEntries``).
2. Writes a thin proxy file for each entry into
   ``recoco/frontend/src/js/plugins/`` - e.g.
   ``src/js/plugins/giphySearch.js`` containing::

       import '/abs/path/to/plugin_giphy/js/giphySearch.js';

3. Writes ``recoco/frontend/plugin-entries.json`` mapping entry name →
   proxy path relative to the Vite source root.

Both generated artefacts are gitignored; they must be regenerated whenever a
plugin is installed or removed.

The core ``vite.config.js`` reads ``plugin-entries.json`` at build time and
adds the proxy files as named Vite inputs automatically - no manual edits
required.

Loading the bundle in a template
----------------------------------

Use ``{% vite_asset %}`` with the proxy path (always under ``js/plugins/``):

.. code-block:: html+django

    {% block js %}
        {{ block.super }}
        {% vite_asset 'js/plugins/giphySearch.js' %}
    {% endblock js %}

The manifest key that ``django-vite`` looks up is the path relative to the
Vite ``root`` (``src/``), i.e. ``js/plugins/giphySearch.js``.

Summary of the full workflow
-----------------------------

.. code-block:: text

    ┌───────────────────────────────────────────────────────────────┐
    │ Plugin repo                                                   │
    │  package.json  →  recocoPlugin.viteEntries                   │
    │  plugin.py     →  vite_entries = {"giphySearch": "js/..."}   │
    │  js/giphySearch.js  (Alpine controller, own npm deps)        │
    └────────────────────────────┬──────────────────────────────────┘
                                 │  python manage.py collect_plugin_vite_entries
                                 ▼
    ┌───────────────────────────────────────────────────────────────┐
    │ Core repo  (recoco/frontend/)                                 │
    │  plugin-entries.json              (gitignored, generated)    │
    │  src/js/plugins/giphySearch.js    (gitignored, proxy file)   │
    │  vite.config.js  reads plugin-entries.json automatically     │
    └───────────────────────────────────────────────────────────────┘
                                 │  npm run build / npm run dev
                                 ▼
    ┌───────────────────────────────────────────────────────────────┐
    │ Output                                                        │
    │  dist/  contains the built plugin bundle                      │
    │  {% vite_asset 'js/plugins/giphySearch.js' %}                │
    └───────────────────────────────────────────────────────────────┘


Activation
==========

Plugins are activated per tenant through the ``SiteConfiguration`` admin:

1. Install the plugin package into the dev environment::

    uv pip install -e ./plugins/plugin_giphy

2. Add ``plugin_giphy`` to ``INSTALLED_APPS`` in the relevant settings file (ie. ``development.py``).

3. Create the tenant schema and run plugin migrations::

    python manage.py migrate_tenant --schema=tenant_paris plugin_giphy

4. If the plugin ships JavaScript, install its npm deps and generate Vite proxies::

    cd /path/to/plugin-giphy && npm install
    cd /path/to/recoco && python manage.py collect_plugin_vite_entries

5. Rebuild the frontend (only when deploying)::

    cd recoco/frontend && npm run build

6. In the Django admin, edit the ``SiteConfiguration`` for the target site:

   - Set ``schema_name`` to ``tenant_paris``.
   - Add ``"plugin_giphy"`` to the ``enabled_plugins`` JSON list.

On the next request, the middleware switches the PostgreSQL ``search_path``
to ``tenant_paris, public`` and the ``PluginURLResolver`` exposes the plugin
routes exclusively to that tenant.
