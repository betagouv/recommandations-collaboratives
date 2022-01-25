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

.. autofunction:: urbanvitaliz.apps.projects.utils.can_administrate_project


.. autofunction:: urbanvitaliz.apps.projects.utils.can_manage_project


Roles
-----

* Switchtender: is a switchtender and can assign herself to a project
* Regional Actor: means this user is a localized actor for a given project


.. autofunction:: urbanvitaliz.apps.projects.context_processors.is_switchtender_processor

.. autofunction:: urbanvitaliz.apps.projects.utils.get_regional_actors_for_project
.. autofunction:: urbanvitaliz.apps.projects.utils.is_regional_actor_for_project
