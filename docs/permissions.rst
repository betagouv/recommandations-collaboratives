Permissions and Roles
=====================

Projects
--------

There are 3 permission levels::
 - **Read-only** : you can only see some info (mostly public) about a project.
 - **Manage** : you can manage a project, except for internal team data.
 - **Administrate** : you can administrate most of the data of a project, except for
   site-level administrator data

Utilities and low level functions that matches permission levels:

.. autofunction:: recoco.apps.projects.utils.can_administrate_project


Roles
-----

* Switchtender: is a switchtender and can assign herself to a project
* Regional Actor: means this user is a localized actor for a given project


.. autofunction:: recoco.apps.projects.context_processors.is_switchtender_processor

.. autofunction:: recoco.apps.projects.utils.get_regional_actors_for_project
.. autofunction:: recoco.apps.projects.utils.is_regional_actor_for_project


REST API permissions reference
-------------------------------

``docs/api_permissions.yaml`` is a code-verified reference matrix of every
REST API viewset/endpoint, the permission actually enforced for each
verb/action, the roles allowed, and the tests exercising it. It also holds
a ground-truth ``roles:`` section mapping each role (``site:staff``,
``project:advisor``, ...) to the permissions it actually grants in code,
derived from ``SITE_GROUP_PERMISSIONS`` (:mod:`recoco.apps.home.models`)
for site-scoped roles and ``assign_collaborator``/``assign_advisor``/
``assign_observer`` (:mod:`recoco.apps.projects.utils`) for project-scoped
ones.

Two distinct role mechanisms are documented there:

* ``site:*`` roles — persistent, per-tenant (Site) Django Groups that
  statically compose a fixed set of permissions.
* ``project:*`` roles — **not** Groups: a runtime, per-object grant
  assigned directly to a user via ``guardian.assign_perm(perm, user,
  project)`` when they become a collaborator/advisor/observer on a
  specific project. Notably, ``project:observer`` is granted the exact
  same permission set as ``project:advisor`` in code — the name implies a
  read-only restriction that does not actually exist.

Several rendered PDF views of this matrix are also generated into
``docs/``: ``api_permissions.pdf`` (the full matrix), ``api_roles_matrix.pdf``
(a flat view/verb/roles table), ``api_roles_check.pdf`` (the roles-vs-code
findings), and ``api_permissions_problems.pdf`` (a punch list of gaps found
during the audit).

The plain-language Access Control Matrix below is generated the same way
(``scripts/generate_acm.py``, from ``docs/api_permissions.yaml``'s
``roles:`` section and the capability mapping in
``docs/acm_capabilities.yaml``) and is embedded directly here, in addition
to the standalone ``api_acm.pdf`` for sharing/printing.

.. include:: acm_generated.rst

Checking the matrix for staleness
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because this matrix is hand-verified against the code at a point in time,
it can drift out of date as views and tests are edited.
``scripts/check_permissions_matrix.py`` detects that drift: for every
entry it resolves the enclosing Python symbol (class/method/function,
decorators included, since e.g. ``@action(..., permission_classes=[...])``
often carries permission-relevant configuration itself) via the ``ast``
module, then compares that symbol's exact source text between the
matrix's ``verified_commit`` baseline (``git show <sha>:<path>``) and the
current working tree. Only entries whose *resolved symbol* actually
changed are flagged — unrelated edits elsewhere in the same file, or line
numbers shifting because of them, do not cause noise.

.. code-block:: bash

   # full report
   uv run python scripts/check_permissions_matrix.py

   # only what needs review
   uv run python scripts/check_permissions_matrix.py --only-stale

   # machine-readable output, e.g. for CI
   uv run python scripts/check_permissions_matrix.py --json

   # once every flagged entry has been re-verified, record the new baseline
   uv run python scripts/check_permissions_matrix.py --update

The exit code is ``1`` if anything needs review, so the ``--only-stale``
or ``--json`` forms can gate a pre-commit hook or CI job. ``--update``
refuses to run while anything is still flagged, and edits only the single
top-level ``verified_commit:`` line in place — it never re-serializes the
whole YAML file, to preserve its hand-written comments and formatting.

An individual viewset, action, or endpoint can opt out of checking with
``skip_check: true`` — used for entries whose ``code_ref`` points at
something outside our code (a third-party import, for example) that the
symbol resolver has nothing to resolve.
