"""
Project endpoints that bots reach with a service API key: creating a project
that skips moderation, and attaching people to a project.

Only bots may use them, with a service API key and a permission granted on the
site: not staff, site admins (who hold every site permission) or superusers.
"""

import pytest
from actstream.models import Action
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from notifications import models as notifications_models

from recoco import verbs
from recoco.apps.geomatics import models as geomatics_models

from .. import models

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
        reverse("projects-members-create", args=[project.id]), data=JANE
    )

    assert response.status_code == 403
    assert not models.ProjectMember.objects.exists()


@pytest.mark.django_db
def test_site_admin_cannot_attach_member(api_client, admin_user, project):
    api_client.force_authenticate(admin_user)

    response = api_client.post(
        reverse("projects-members-create", args=[project.id]), data=JANE
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
        reverse("projects-members-create", args=[other_project.id]), data=JANE
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
        reverse("projects-members-create", args=[project.id]),
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
        reverse("projects-members-create", args=[project.id]),
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
            reverse("projects-members-create", args=[project.id]), data=JANE
        ).status_code
        == 201
    )
    assert (
        bot_client.post(
            reverse("projects-members-create", args=[project.id]), data=JANE
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
        reverse("projects-members-create", args=[project.id]), data=JANE
    )

    assert response.status_code == 400
    assert "email" in response.data
    assert not models.ProjectMember.objects.exists()
    assert current_site not in jane.profile.sites.all()
