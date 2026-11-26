"""
Project endpoints that bots reach with a service API key: creating a project
that skips moderation, and managing the members of a project (attaching them,
listing them, removing them or their roles, changing the owner).

Only bots may use them, with a service API key and a permission granted on the
site: not staff, site admins (who hold every site permission) or superusers.
"""

import uuid

import pytest
from actstream.models import Action
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from notifications import models as notifications_models
from notifications.signals import notify

from recoco import verbs
from recoco.apps.geomatics import models as geomatics_models

from .. import models, utils

JANE = {"email": "jane@example.com", "role": "COLLABORATOR"}


@pytest.fixture
def commune():
    return baker.make(geomatics_models.Commune, insee="62000")


def project_data(**kwargs):
    return {
        "name": "a project",
        "description": "a description",
        "insee": "62000",
        "owner_email": "owner@example.com",
        **kwargs,
    }


########################################################################
# create project: who may
########################################################################


@pytest.mark.django_db
def test_bot_with_permission_on_another_site_cannot_create_project(
    bot_client, service_account, commune
):
    other_site = baker.make(Site)
    assign_perm("sites.create_projects", service_account, other_site)

    response = bot_client.post(reverse("projects-create"), data=project_data())

    assert response.status_code == 403
    assert not models.Project.objects.exists()


@pytest.mark.django_db
def test_site_admin_cannot_create_project(api_client, admin_user, commune):
    api_client.force_authenticate(admin_user)

    response = api_client.post(reverse("projects-create"), data=project_data())

    assert response.status_code == 403
    assert not models.Project.objects.exists()


########################################################################
# create project: what it does
########################################################################


@pytest.mark.django_db
def test_bot_creates_a_validated_project(
    bot_client, service_account, current_site, commune
):
    assign_perm("sites.create_projects", service_account, current_site)

    response = bot_client.post(
        reverse("projects-create"),
        data=project_data(location="somewhere", owner_email="OWNER@example.com"),
    )

    assert response.status_code == 201

    project = models.Project.objects.get(pk=response.data["id"])
    assert project.name == "a project"
    assert project.description == "a description"
    assert project.commune == commune
    assert project.submitted_by == service_account

    project_site = project.project_sites.get(site=current_site)
    assert project_site.status == "TO_PROCESS"
    assert project_site.is_origin is True

    # the owner account is created on the site, with a lowercased email
    owner = auth_models.User.objects.get(username="owner@example.com")
    assert owner.email == "owner@example.com"
    assert not owner.has_usable_password()
    assert current_site in owner.profile.sites.all()
    assert project.owner == owner

    # the history is kept, but no one is notified
    assert Action.objects.filter(
        actor_object_id=str(service_account.pk), verb=verbs.Project.VALIDATED_BY
    ).exists()
    assert Action.objects.filter(
        actor_object_id=str(owner.pk), verb=verbs.Project.JOINED_OWNER
    ).exists()
    assert not notifications_models.Notification.objects.exists()


@pytest.mark.django_db
def test_project_status_can_be_given(
    bot_client, service_account, current_site, commune
):
    assign_perm("sites.create_projects", service_account, current_site)

    response = bot_client.post(
        reverse("projects-create"), data=project_data(status="IN_PROGRESS")
    )

    assert response.status_code == 201
    assert response.data["status"] == "IN_PROGRESS"
    project = models.Project.objects.get(pk=response.data["id"])
    assert project.project_sites.get(site=current_site).status == "IN_PROGRESS"


@pytest.mark.parametrize("status", ["PRE_DRAFT", "DRAFT", "REJECTED"])
@pytest.mark.django_db
def test_moderation_status_is_rejected(
    bot_client, service_account, current_site, commune, status
):
    assign_perm("sites.create_projects", service_account, current_site)

    response = bot_client.post(
        reverse("projects-create"), data=project_data(status=status)
    )

    assert response.status_code == 400
    assert "status" in response.data
    assert not models.Project.objects.exists()


@pytest.mark.django_db
def test_unknown_insee_code_is_rejected(bot_client, service_account, current_site):
    assign_perm("sites.create_projects", service_account, current_site)

    response = bot_client.post(
        reverse("projects-create"), data=project_data(insee="00000")
    )

    assert response.status_code == 400
    assert "insee" in response.data
    assert not models.Project.objects.exists()


@pytest.mark.django_db
def test_owner_account_of_another_site_is_rejected(
    bot_client, service_account, current_site, commune
):
    assign_perm("sites.create_projects", service_account, current_site)
    other_site = baker.make(Site)
    owner = baker.make(auth_models.User, username="owner@example.com")
    owner.profile.sites.add(other_site)

    response = bot_client.post(reverse("projects-create"), data=project_data())

    assert response.status_code == 400
    assert "owner_email" in response.data
    assert not models.Project.objects.exists()
    assert current_site not in owner.profile.sites.all()


########################################################################
# attach people to a project: who may
########################################################################


@pytest.mark.django_db
def test_bot_with_permission_on_another_site_cannot_attach_member(
    bot_client, service_account, project
):
    other_site = baker.make(Site)
    assign_perm("sites.manage_project_members", service_account, other_site)

    response = bot_client.post(
        reverse("projects-members-list", args=[project.id]), data=JANE
    )

    assert response.status_code == 403
    assert not models.ProjectMember.objects.exists()


@pytest.mark.django_db
def test_site_admin_cannot_attach_member(api_client, admin_user, project):
    api_client.force_authenticate(admin_user)

    response = api_client.post(
        reverse("projects-members-list", args=[project.id]), data=JANE
    )

    assert response.status_code == 403
    assert not models.ProjectMember.objects.exists()


@pytest.mark.django_db
def test_project_of_another_site_is_not_found(
    bot_client, service_account, current_site, make_project
):
    assign_perm("sites.manage_project_members", service_account, current_site)
    other_site = baker.make(Site)
    other_project = make_project(site=other_site)

    response = bot_client.post(
        reverse("projects-members-list", args=[other_project.id]), data=JANE
    )

    assert response.status_code == 404
    assert not models.ProjectMember.objects.exists()


########################################################################
# attach people to a project: what it does
########################################################################


@pytest.mark.django_db
def test_bot_attaches_a_collaborator(
    bot_client, service_account, current_site, project
):
    assign_perm("sites.manage_project_members", service_account, current_site)

    response = bot_client.post(
        reverse("projects-members-list", args=[project.id]),
        data={"email": "JANE@example.com", "role": "COLLABORATOR"},
    )

    assert response.status_code == 201

    # the account is created on the site, with a lowercased email
    member = auth_models.User.objects.get(username="jane@example.com")
    assert current_site in member.profile.sites.all()

    membership = models.ProjectMember.objects.get(project=project, member=member)
    assert membership.is_owner is False
    assert member.has_perm("projects.use_tasks", project)

    # the history is kept, but no one is notified
    assert Action.objects.filter(
        actor_object_id=str(member.pk), verb=verbs.Project.JOINED_BY_INVITATION
    ).exists()
    assert not notifications_models.Notification.objects.exists()


@pytest.mark.parametrize(
    "role,is_observer,verb",
    [
        ("SWITCHTENDER", False, verbs.Project.BECAME_ADVISOR),
        ("OBSERVER", True, verbs.Project.BECAME_OBSERVER),
    ],
)
@pytest.mark.django_db
def test_bot_attaches_an_advisor(
    bot_client,
    service_account,
    current_site,
    staff_user,
    project,
    role,
    is_observer,
    verb,
):
    assign_perm("sites.manage_project_members", service_account, current_site)
    staff_user.username = "john@example.com"
    staff_user.save()

    response = bot_client.post(
        reverse("projects-members-list", args=[project.id]),
        data={"email": "john@example.com", "role": role},
    )

    assert response.status_code == 201

    switchtending = models.ProjectSwitchtender.objects.get(
        project=project, switchtender=staff_user, site=current_site
    )
    assert switchtending.is_observer is is_observer
    assert staff_user.has_perm("projects.view_project", project)
    assert Action.objects.filter(actor_object_id=str(staff_user.pk), verb=verb).exists()
    assert not notifications_models.Notification.objects.exists()


@pytest.mark.django_db
def test_attaching_again_writes_no_new_history(
    bot_client, service_account, current_site, project
):
    assign_perm("sites.manage_project_members", service_account, current_site)

    assert (
        bot_client.post(
            reverse("projects-members-list", args=[project.id]), data=JANE
        ).status_code
        == 201
    )
    assert (
        bot_client.post(
            reverse("projects-members-list", args=[project.id]), data=JANE
        ).status_code
        == 201
    )

    assert models.ProjectMember.objects.filter(project=project).count() == 1
    assert Action.objects.filter(verb=verbs.Project.JOINED_BY_INVITATION).count() == 1


@pytest.mark.django_db
def test_member_account_of_another_site_is_rejected(
    bot_client, service_account, current_site, project
):
    assign_perm("sites.manage_project_members", service_account, current_site)
    other_site = baker.make(Site)
    jane = baker.make(auth_models.User, username="jane@example.com")
    jane.profile.sites.add(other_site)

    response = bot_client.post(
        reverse("projects-members-list", args=[project.id]), data=JANE
    )

    assert response.status_code == 400
    assert "email" in response.data
    assert not models.ProjectMember.objects.exists()
    assert current_site not in jane.profile.sites.all()


########################################################################
# list the members of a project, remove them, change its owner: who may
########################################################################


@pytest.fixture
def make_member(current_site):
    """Return a factory attaching someone to a project with the given role"""

    def _make_member(project, role="COLLABORATOR", email=None, is_owner=False):
        email = email or f"{uuid.uuid4().hex}@example.com"
        user = baker.make(auth_models.User, username=email, email=email)
        user.profile.sites.add(current_site)

        if is_owner:
            utils.assign_collaborator(user, project, is_owner=True)
        else:
            utils.assign_role(user, project, role, current_site)

        return user

    return _make_member


@pytest.fixture
def manager_client(bot_client, service_account, current_site):
    """A bot client allowed to manage the members of the projects of the site"""
    assign_perm("sites.manage_project_members", service_account, current_site)
    return bot_client


# for each endpoint: how to call it on a project, for the given collaborator
MEMBERSHIP_CALLS = {
    "list": lambda c, p, u: c.get(reverse("projects-members-list", args=[p.id])),
    "remove_member": lambda c, p, u: c.delete(
        reverse("projects-members-detail", args=[p.id, u.username])
    ),
    "remove_role": lambda c, p, u: c.delete(
        reverse("projects-members-role-detail", args=[p.id, u.username, "COLLABORATOR"])
    ),
    "change_owner": lambda c, p, u: c.put(
        reverse("projects-owner-detail", args=[p.id]), data={"email": u.username}
    ),
}


def assert_membership_unchanged(project, owner, collaborator):
    assert project.owner == owner
    assert models.ProjectMember.objects.filter(
        project=project, member=collaborator
    ).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
def test_anonymous_cannot_manage_members(api_client, project, make_member, call):
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](api_client, project, collaborator)

    assert response.status_code in (401, 403)
    assert_membership_unchanged(project, owner, collaborator)


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
def test_bot_without_permission_cannot_manage_members(
    bot_client, project, make_member, call
):
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](bot_client, project, collaborator)

    assert response.status_code == 403
    assert_membership_unchanged(project, owner, collaborator)


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
def test_bot_with_permission_on_another_site_cannot_manage_members(
    bot_client, service_account, project, make_member, call
):
    assign_perm("sites.manage_project_members", service_account, baker.make(Site))
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](bot_client, project, collaborator)

    assert response.status_code == 403
    assert_membership_unchanged(project, owner, collaborator)


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
@pytest.mark.parametrize("username", ["staff_user", "admin_user"])
def test_staff_and_admin_cannot_manage_members(
    request, api_client, project, make_member, call, username
):
    api_client.force_authenticate(request.getfixturevalue(username))
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](api_client, project, collaborator)

    assert response.status_code == 403
    assert_membership_unchanged(project, owner, collaborator)


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
def test_superuser_cannot_manage_members(api_client, project, make_member, call):
    api_client.force_authenticate(baker.make(auth_models.User, is_superuser=True))
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](api_client, project, collaborator)

    assert response.status_code == 403
    assert_membership_unchanged(project, owner, collaborator)


@pytest.mark.django_db
@pytest.mark.parametrize("call", MEMBERSHIP_CALLS.keys())
def test_members_of_a_project_of_another_site_are_not_found(
    manager_client, make_project, make_member, call
):
    project = make_project(site=baker.make(Site))
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    response = MEMBERSHIP_CALLS[call](manager_client, project, collaborator)

    assert response.status_code == 404
    assert_membership_unchanged(project, owner, collaborator)


########################################################################
# list the members of a project, and remove them or their roles
########################################################################


@pytest.mark.django_db
def test_bot_lists_the_members(current_site, manager_client, project, make_member):
    owner = make_member(project, email="owner@example.com", is_owner=True)
    collaborator = make_member(project, email="jane@example.com")
    advisor = make_member(project, "SWITCHTENDER", email="john@example.com")
    observer = make_member(project, "OBSERVER", email="jim@example.com")

    # someone holding two roles is listed once
    utils.assign_role(collaborator, project, "SWITCHTENDER", current_site)

    # an advisor on another site is not listed
    other_site = baker.make(Site)
    utils.assign_advisor(baker.make(auth_models.User), project, site=other_site)

    response = manager_client.get(reverse("projects-members-list", args=[project.id]))

    assert response.status_code == 200
    assert response.data[0] == {
        "email": owner.email,
        "first_name": owner.first_name,
        "last_name": owner.last_name,
        "roles": ["COLLABORATOR"],
        "is_owner": True,
    }
    assert [(m["email"], m["roles"], m["is_owner"]) for m in response.data] == [
        (owner.email, ["COLLABORATOR"], True),
        (collaborator.email, ["COLLABORATOR", "SWITCHTENDER"], False),
        (observer.email, ["OBSERVER"], False),
        (advisor.email, ["SWITCHTENDER"], False),
    ]


@pytest.mark.django_db
def test_bot_removes_the_collaborator_role(
    manager_client, current_site, project, make_member
):
    collaborator = make_member(project, email="jane@example.com")
    utils.assign_role(collaborator, project, "SWITCHTENDER", current_site)

    # the email of the url is case insensitive
    url = reverse(
        "projects-members-role-detail",
        args=[project.id, "JANE@example.com", "COLLABORATOR"],
    )
    response = manager_client.delete(url)

    assert response.status_code == 204

    assert utils.get_roles(collaborator, project, current_site) == ["SWITCHTENDER"]
    # a permission shared by both roles is kept
    assert collaborator.has_perm("projects.manage_collaborators", project)


@pytest.mark.django_db
def test_bot_removes_the_observer_role(
    manager_client, current_site, project, make_member
):
    collaborator = make_member(project)
    utils.assign_role(collaborator, project, "OBSERVER", current_site)

    url = reverse(
        "projects-members-role-detail",
        args=[project.id, collaborator.username, "OBSERVER"],
    )
    response = manager_client.delete(url)

    assert response.status_code == 204

    assert utils.get_roles(collaborator, project, current_site) == ["COLLABORATOR"]
    # a permission shared by both roles is kept
    assert collaborator.has_perm("projects.view_project", project)
    # a permission of the removed role only is not
    assert not collaborator.has_perm("projects.use_private_notes", project)


@pytest.mark.django_db
def test_role_not_held_is_not_found(manager_client, current_site, project, make_member):
    advisor = make_member(project, "SWITCHTENDER")

    for role in ("COLLABORATOR", "OBSERVER", "UNKNOWN"):
        url = reverse(
            "projects-members-role-detail", args=[project.id, advisor.username, role]
        )
        assert manager_client.delete(url).status_code == 404

    assert utils.get_roles(advisor, project, current_site) == ["SWITCHTENDER"]


@pytest.mark.django_db
def test_bot_removes_a_member(manager_client, current_site, project, make_member):
    owner = make_member(project, is_owner=True)
    collaborator = make_member(project)

    # to check they are cleaned up when the member is removed
    notify.send(sender=owner, recipient=collaborator, verb="a verb", target=project)
    baker.make(
        models.UserProjectStatus, site=current_site, user=collaborator, project=project
    )

    url = reverse("projects-members-detail", args=[project.id, collaborator.username])
    response = manager_client.delete(url)

    assert response.status_code == 204

    assert not models.ProjectMember.objects.filter(
        project=project, member=collaborator
    ).exists()
    assert not models.ProjectSwitchtender.objects.filter(
        project=project, switchtender=collaborator
    ).exists()
    assert not collaborator.has_perm("projects.view_project", project)
    assert not notifications_models.Notification.objects.filter(
        recipient=collaborator
    ).exists()
    assert not models.UserProjectStatus.objects.filter(
        user=collaborator, project=project
    ).exists()

    # the other members are kept
    assert models.ProjectMember.objects.filter(project=project, member=owner).exists()


@pytest.mark.django_db
def test_unknown_member_is_not_found(manager_client, project, make_member):
    make_member(project)
    make_member(project, "SWITCHTENDER")

    url = reverse("projects-members-detail", args=[project.id, "unknown@example.com"])

    assert manager_client.delete(url).status_code == 404

    # nobody else is removed instead
    assert models.ProjectMember.objects.filter(project=project).count() == 1
    assert models.ProjectSwitchtender.objects.filter(project=project).count() == 1


@pytest.mark.django_db
def test_owner_is_not_removed(manager_client, current_site, project, make_member):
    owner = make_member(project, is_owner=True)
    utils.assign_role(owner, project, "SWITCHTENDER", current_site)

    url = reverse("projects-members-detail", args=[project.id, owner.username])
    assert manager_client.delete(url).status_code == 400

    url = reverse(
        "projects-members-role-detail",
        args=[project.id, owner.username, "COLLABORATOR"],
    )
    assert manager_client.delete(url).status_code == 400

    assert project.owner == owner

    # yet the owner can stop being an advisor
    url = reverse(
        "projects-members-role-detail",
        args=[project.id, owner.username, "SWITCHTENDER"],
    )
    assert manager_client.delete(url).status_code == 204

    assert utils.get_roles(owner, project, current_site) == ["COLLABORATOR"]
    assert owner.has_perm("projects.use_tasks", project)


########################################################################
# change the owner of a project
########################################################################


@pytest.mark.django_db
def test_bot_changes_the_owner(manager_client, project, make_member):
    former_owner = make_member(project, is_owner=True)
    collaborator = make_member(project)
    make_member(project, "SWITCHTENDER")

    collaborator.profile.phone_no = "0102030405"
    collaborator.profile.save()

    # the email is case insensitive
    url = reverse("projects-owner-detail", args=[project.id])
    response = manager_client.put(url, data={"email": collaborator.username.upper()})

    assert response.status_code == 200
    assert response.data == {"email": collaborator.username.upper()}

    assert project.owner == collaborator

    # the former owner remains a participant
    assert models.ProjectMember.objects.filter(
        project=project, member=former_owner, is_owner=False
    ).exists()

    project.refresh_from_db()
    assert project.phone == "0102030405"

    # the advisor and both members are notified
    assert (
        notifications_models.Notification.objects.filter(
            verb=verbs.Project.NEW_OWNER
        ).count()
        == 3
    )


@pytest.mark.django_db
def test_unknown_owner_account_is_created(
    current_site, manager_client, project, make_member
):
    former_owner = make_member(project, is_owner=True)

    url = reverse("projects-owner-detail", args=[project.id])
    response = manager_client.put(url, data={"email": "jane@example.com"})

    assert response.status_code == 200

    owner = auth_models.User.objects.get(username="jane@example.com")
    assert current_site in owner.profile.sites.all()

    # the new owner is made a participant of the project
    assert project.owner == owner
    assert owner.has_perm("projects.use_tasks", project)

    assert models.ProjectMember.objects.filter(
        project=project, member=former_owner, is_owner=False
    ).exists()


@pytest.mark.django_db
def test_owner_account_of_another_site_is_rejected_as_new_owner(
    current_site, manager_client, project, make_member
):
    owner = make_member(project, is_owner=True)
    jane = baker.make(auth_models.User, username="jane@example.com")
    jane.profile.sites.add(baker.make(Site))

    url = reverse("projects-owner-detail", args=[project.id])
    response = manager_client.put(url, data={"email": "jane@example.com"})

    assert response.status_code == 400
    assert "email" in response.data
    assert project.owner == owner
    assert current_site not in jane.profile.sites.all()


@pytest.mark.django_db
def test_current_owner_is_a_noop(manager_client, project, make_member):
    owner = make_member(project, is_owner=True)
    make_member(project)

    url = reverse("projects-owner-detail", args=[project.id])
    response = manager_client.put(url, data={"email": owner.username})

    assert response.status_code == 200
    assert project.owner == owner
    assert models.ProjectMember.objects.filter(project=project).count() == 2
    assert not notifications_models.Notification.objects.exists()
