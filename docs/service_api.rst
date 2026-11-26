Service API
###########

Service API endpoints let another program, rather than a person, act on a
portal. The caller is a *bot*: an account that authenticates with a service API
key and nothing else.

This page is for developers adding such an endpoint: what is already available,
and the pattern to follow.

.. contents:: Table of Contents
   :local:
   :depth: 2


Overview
========

- **A key belongs to one bot and one site.** It is refused on any other site.
- **A view has to opt in.** Keys are not part of
  ``DEFAULT_AUTHENTICATION_CLASSES``, so a view refuses them unless it says
  otherwise.
- **A key gives no right by itself.** Rights are permissions granted to the bot
  on a site.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Building block
     - Use it to
   * - ``api_keys.authentication.WITH_SERVICE_API_KEY``
     - let keys reach a view, on top of the usual login methods
   * - ``api_keys.permissions.IsServiceAPIKey``
     - reserve a view to bots
   * - ``home.utils.find_verified_user_for_site``
     - find the person behind an email, without creating anything
   * - ``home.utils.get_or_create_user_for_site``
     - same, creating the account if there is none
   * - ``home.utils.UnavailableAccountException``
     - know that an account exists but cannot be used here
   * - ``validate_email_for_site`` (``recoco.rest_api.serializers``)
     - refuse such an account in a serializer
   * - ``bot_key``, ``bot_client``, ``service_account`` (``conftest.py``)
     - test as a bot

All of these live under ``recoco.apps``, unless stated otherwise.


Bots and keys
=============

Bots are managed with the ``bot`` command. The admin only lists keys.

.. code-block:: bash

    # a new bot, or another site for an existing bot
    python manage.py bot create --name my-bot --site portal.example.com

    # replace the key of a site, the previous one is revoked
    python manage.py bot renew --name my-bot --site portal.example.com

    # deactivate the bot and revoke all its keys
    python manage.py bot disable --name my-bot

    # bring it back, with a new key for one site
    python manage.py bot enable --name my-bot --site portal.example.com

The key is printed once and cannot be read again. The client sends it in the
``Authorization`` header, and can check it on ``auth-check``:

.. code-block:: bash

    curl -H "Authorization: Api-Key $KEY" https://portal.example.com/api/auth/check/

A key skips 2FA, so a bot never holds human privileges: no password, email,
ProConnect link, staff or superuser flag, global permission, nor staff, admin or
advisor group. See ``recoco/apps/home/bots.py`` for the rules.

Granting a right
----------------

Give the bot an object permission on the site:

.. code-block:: python

    from guardian.shortcuts import assign_perm

    assign_perm("sites.manage_project_contacts", bot, site)

A global permission would apply to every site, so it is refused for bots. The
key and the permission are both per site: a bot working on two sites needs both
of them twice.


Adding an endpoint
==================

The example below is fictional: it lets a bot attach a contact, given by email,
to a project.

1. The permission
-----------------

Declare one permission per action in ``create_site_permissions``, in
``recoco/apps/projects/models.py``:

.. code-block:: python

    auth_models.Permission.objects.get_or_create(
        codename="manage_project_contacts",
        name="Can attach contacts to projects for site",
        content_type=site_ct,
    )

If only bots may do it, leave it out of ``SITE_GROUP_PERMISSIONS``: no human
group should hold it.

Then write one plain permission class, next to the views:

.. code-block:: python

    class CanManageProjectContacts(permissions.BasePermission):
        def has_permission(self, request, view):
            return has_perm(
                request.user, "sites.manage_project_contacts", request.site
            )

Always check against ``request.site``. ``has_perm`` trusts the object it is
given, and passing an object of another site can wrongly grant access.

2. The view
-----------

.. code-block:: python

    class ProjectContactCreate(CreateAPIView):
        """Attach a contact to a project of the current site"""

        authentication_classes = WITH_SERVICE_API_KEY
        permission_classes = [IsServiceAPIKey, CanManageProjectContacts]
        serializer_class = ProjectContactSerializer

        def perform_create(self, serializer):
            project = get_object_or_404(models.Project.on_site, pk=self.kwargs["pk"])
            serializer.save(project=project)

``authentication_classes``
    Who can *log in* here. Without ``WITH_SERVICE_API_KEY``, a key is ignored.
    It adds keys to the usual methods and does not exclude people.

``IsServiceAPIKey``
    Who may *go through*: bots only. ``has_perm`` cannot tell a bot from a
    person, as site admins hold every permission of their site and superusers
    hold them all.

``CanManageProjectContacts``
    What the bot is *allowed to do*. ``IsServiceAPIKey`` is not enough: any key
    of the site would go through.

Read objects through ``on_site``, so that those of another site answer ``404``.

For an endpoint open to both people and bots, drop ``IsServiceAPIKey`` and keep
the other two. Site admins and superusers then go through as well.

For a function view:

.. code-block:: python

    @api_view(["POST"])
    @authentication_classes(WITH_SERVICE_API_KEY)
    @permission_classes([IsServiceAPIKey, CanManageProjectContacts])
    def project_contact_create(request, pk): ...

3. The serializer
-----------------

.. code-block:: python

    class ProjectContactSerializer(BaseSerializerMixin, serializers.Serializer):
        email = serializers.EmailField(max_length=150)

        def validate_email(self, value):
            return validate_email_for_site(value, self.current_site)

        @transaction.atomic
        def create(self, validated_data):
            user = get_or_create_user_for_site(
                validated_data["email"], self.current_site
            )
            assign_collaborator(user, validated_data["project"])
            return validated_data

``BaseSerializerMixin`` provides ``current_site`` and ``current_user``, the
latter being the bot. ``validate_email_for_site`` turns a refusal into a
``400``; the account is only created once all the data is valid.

4. The route
------------

In ``recoco/rest_api/urls.py``:

.. code-block:: python

    path(
        "projects/<int:pk>/contacts/",
        projects_rest.ProjectContactCreate.as_view(),
        name="projects-contacts-create",
    ),


Accounts given by email
=======================

Use the two helpers instead of querying ``User`` by email.

.. list-table::
   :header-rows: 1
   :widths: 50 25 25

   * - The email matches
     - ``find_verified_...``
     - ``get_or_create_...``
   * - nobody
     - ``None``
     - new account
   * - an account of the site
     - the account
     - the account
   * - an account of another site
     - exception
     - exception
   * - a bot or a disabled account
     - exception
     - exception

The exception is ``UnavailableAccountException``. It is raised as soon as one of
the matching accounts cannot be used.

The username and main email are matched regardless of case. A secondary address
only counts once verified: anyone can add the address of someone else to their
account, and would then receive what is meant for that person.

.. note::

    The username and main email are trusted as is: "verified" in
    ``find_verified_user_for_site`` is about secondary addresses. Finding an
    account does not prove that its owner confirmed the main email.

A new account has a lowercased email, no usable password, and access to the
site. Nobody is notified by the helpers.


Responses
=========

.. list-table::
   :header-rows: 1
   :widths: 15 85

   * - Status
     - When
   * - ``201``
     - the object was created
   * - ``400``
     - invalid data, or an account that cannot be used here
   * - ``403``
     - missing, invalid, expired or revoked key, key of another site, caller
       who is not a bot, or missing permission
   * - ``404``
     - unknown object, or object of another site
   * - ``429``
     - too many requests

An authentication failure answers ``403`` and not ``401``: ``401`` needs a
``WWW-Authenticate`` header, taken from the first authentication class, and
``SessionAuthentication`` has none.

Bots follow the ``user_but_exception`` rate, except those in a
``<site>_trusted_bot`` group. That group only lifts the rate limit, it gives no
permission.


Testing
=======

``recoco/apps/api_keys/tests/test_opted_in_views.py`` finds every view that
accepts keys, and checks that a key without any right gets a ``403``. A new view
is covered without changing that file, provided its permissions are checked
before objects are looked up. Do not add it to ``OPEN_TO_ANY_KEY`` to make the
test pass.

Use the shared fixtures: ``bot_client`` is an API client using ``bot_key``, the
key of ``service_account`` on ``current_site``. The bot holds no right until the
test grants one.

.. code-block:: python

    @pytest.mark.django_db
    def test_bot_attaches_contact(
        bot_client, service_account, current_site, make_project
    ):
        project = make_project(site=current_site)
        assign_perm("sites.manage_project_contacts", service_account, current_site)

        response = bot_client.post(
            reverse("projects-contacts-create", args=[project.pk]),
            data={"email": "jane@example.com"},
        )

        assert response.status_code == 201
        assert project.members.filter(username="jane@example.com").exists()

Each endpoint should test that:

- a bot with the permission succeeds;
- a bot without it, or holding it on another site only, gets a ``403``;
- anonymous, staff, site admins and superusers get a ``403`` (bot-only views);
- an object of another site gets a ``404``;
- an account that cannot be used gets a ``400``, and nothing is created.

Assert the exact status code.


Checklist
=========

- ``authentication_classes = WITH_SERVICE_API_KEY``
- ``IsServiceAPIKey`` first, if reserved to bots
- one permission class, checked against ``request.site``
- objects read through ``on_site``
- people found with the helpers, and emails checked with
  ``validate_email_for_site``
- several writes wrapped in ``transaction.atomic``
- a docstring on the view: it is shown in the OpenAPI schema
- tests for each refusal
