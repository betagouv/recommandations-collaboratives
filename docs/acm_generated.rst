.. GENERATED FILE -- do not edit by hand.
   Regenerate with: uv run python scripts/generate_acm.py

Who can do what, on this platform
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This table explains, in plain terms, what each type of user is allowed to do. It does not describe how it is enforced in the software -- it describes the end result. Each row is a capability; each column is a type of user ("role"), identified by a short code. **Yes** means that role can fully do it, **Partly** means they can do part of it (see the notes below the table), and **No** means they cannot do it at all.

Roles
"""""

* **R1 -- Public visitor** (not logged in)
* **R2 -- Any logged-in user** (no special role)
* **R3 -- Project collaborator** (project awaiting validation)
* **R4 -- Project collaborator** (project validated)
* **R5 -- Project advisor** (incl. "observer" advisors -- see note)
* **R6 -- Site coordinator** (regional/site-wide advisor)
* **R7 -- Platform staff** (site-wide)
* **R8 -- Platform administrator** (site-wide)

Access table
""""""""""""

.. list-table::
   :header-rows: 1
   :widths: 30 8 8 8 8 8 8 8 8

   * - Capability
     - R1
     - R2
     - R3
     - R4
     - R5
     - R6
     - R7
     - R8
   * - Browse the public resource catalog
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
   * - Use their own account (profile, notifications)
     - No
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
     - Yes
   * - See a project they belong to
     - No
     - No
     - Yes
     - Yes
     - Yes
     - No
     - No
     - No
   * - Take part in that project's discussion (read & post)
     - No
     - No
     - Yes
     - Yes
     - Yes
     - No
     - No
     - No
   * - See that project's internal, advisor-only notes
     - No
     - No
     - No
     - No
     - Yes
     - No
     - No
     - No
   * - View & propose recommendations
     - No
     - No
     - Partly
     - Yes
     - Yes
     - No
     - No
     - No
   * - Manage recommendations, documents & team members
     - No
     - No
     - No
     - Partly
     - Yes
     - No
     - No
     - No
   * - See & approve the full list of projects site-wide
     - No
     - No
     - No
     - No
     - No
     - Partly
     - Yes
     - No
   * - Manage the site's resource catalog & address book
     - No
     - No
     - No
     - No
     - No
     - Yes
     - Yes
     - No
   * - Configure the platform
     - No
     - No
     - No
     - No
     - No
     - No
     - No
     - Yes

Notes
"""""

* **Project advisor** -- IDENTICAL permission set to project:advisor — OBSERVER_PERMISSIONS is a direct alias of ADVISOR_PERMISSIONS in code, no restriction is applied despite the "observer" name implying read-only/limited access.
* **View & propose recommendations** -- can view and use existing recommendations, but not create, edit or publish one
* **Manage recommendations, documents & team members** -- can manage documents and invite/manage collaborators, but cannot create, edit or publish recommendations
* **See & approve the full list of projects site-wide** -- can see the full list of projects on the site, but cannot approve or reject new ones

This section is generated automatically (``scripts/generate_acm.py``) from ``docs/api_permissions.yaml``'s code-verified ``roles:`` section and the capability mapping in ``docs/acm_capabilities.yaml``. For the exact technical permission checked on every screen and action, together with the tests that confirm it, see ``docs/api_permissions.yaml`` and ``docs/api_roles_check.pdf``.
