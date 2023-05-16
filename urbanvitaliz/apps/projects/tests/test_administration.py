# encoding: utf-8

"""
Tests for project application / administration

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-12-26 11:54:56 CEST
"""


import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertRedirects

from urbanvitaliz.apps.communication import api as communication_api
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.projects.utils import assign_advisor, assign_collaborator
from urbanvitaliz.utils import login

from .. import models

########################################################################
# Project administration
########################################################################


@pytest.mark.django_db
def test_project_admin_not_available_for_unprivileged_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-administration", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_admin_available_for_advisor(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()
    url = reverse("projects-project-administration", args=[project.id])
    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_update_when_missing_commune(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-administration", args=[project.id])
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "description": "a project description",
        "impediment": "some impediment",
    }

    with login(client) as user:
        assign_perm("change_project", user, project)
        response = client.post(url, data=data)

    project = models.Project.on_site.get(id=project.id)
    assert project.name == data["name"]
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_project_update_commune(request, client):
    old_commune = Recipe(
        geomatics.Commune, name="old town", postal="12345", insee="1234"
    ).make()
    new_commune = Recipe(
        geomatics.Commune, name="new town", postal="7890", insee="789"
    ).make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=old_commune
    ).make()
    url = reverse("projects-project-administration", args=[project.id])

    data = {
        "name": "a project",
        "location": "some place",
        "description": "a project description",
        "postcode": new_commune.postal,
        "insee": new_commune.insee,
    }

    with login(client) as user:
        assign_perm("change_project", user, project)
        response = client.post(url, data=data)

    assert response.status_code == 302

    project = models.Project.objects.get(id=project.pk)
    assert project.commune == new_commune


@pytest.mark.django_db
def test_project_update_accessible_for_advisor(request, client):
    site = get_current_site(request)
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(models.Project, sites=[site], commune=commune).make()
    url = reverse("projects-project-administration", args=[project.id])

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.get(url)

    assertContains(response, "<form")
    assertContains(response, commune.postal)


@pytest.mark.django_db
def test_draft_project_update_not_accessible_for_collaborator(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=commune
    ).make()
    url = reverse("projects-project-administration", args=[project.id])

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_accepted_project_update_accessible_for_collaborator(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune=commune,
        status="TO_PROCESS",
    ).make()
    url = reverse("projects-project-administration", args=[project.id])

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, "<form")
    assertContains(response, commune.postal)


########################################################################
# promote collaborator referent
########################################################################


@pytest.mark.django_db
def test_promote_referent_not_available_is_post_only(request, client):

    url = reverse("projects-project-promote-referent", args=[0, 0])
    with login(client):
        response = client.get(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_promote_referent_not_available_for_unprivileged_users(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(site)

    baker.make(
        projects_models.ProjectMember, project=project, member=crm_user, is_owner=False
    )

    url = reverse("projects-project-promote-referent", args=[project.id, crm_user.id])
    with login(client):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_promote_referent_prevent_cross_site_promotion(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    other = baker.make(site_models.Site)
    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(other)

    baker.make(
        projects_models.ProjectMember, project=project, member=crm_user, is_owner=False
    )

    url = reverse("projects-project-promote-referent", args=[project.id, crm_user.id])
    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_promote_referent_available_for_advisor(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(site)

    owner = baker.make(projects_models.ProjectMember, project=project, is_owner=False)
    member = baker.make(
        projects_models.ProjectMember, project=project, member=crm_user, is_owner=False
    )

    url = reverse("projects-project-promote-referent", args=[project.id, crm_user.id])
    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 302

    owner.refresh_from_db()
    assert owner.is_owner is False
    member.refresh_from_db()
    assert member.is_owner is True


#####################################################################
# Removing collaborators from project
#####################################################################


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(request, client):
    site = get_current_site(request)

    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project = baker.make(
        models.Project,
        sites=[site],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, membership.member.email],
    )

    with login(client) as user:
        assign_advisor(user, project, site=site)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert membership in project.projectmember_set.all()

    update_url = reverse("projects-project-administration", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_collaborator_can_remove_other_collaborator_from_project(request, client):
    site = get_current_site(request)
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.email],
    )

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url)

    assert response.status_code == 302
    assert "login" not in response.url  # not a simple redirect to login

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.projectmember_set.all()


@pytest.mark.django_db
def test_advisor_can_remove_collaborator_from_project(request, client):
    site = get_current_site(request)
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.email],
    )

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.members.all()


@pytest.mark.django_db
def test_staff_can_remove_collaborator_from_project(request, client):
    site = get_current_site(request)
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.email],
    )

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.members.all()


@pytest.mark.django_db
def test_unprivileged_user_cannot_remove_collaborator_from_project(request, client):
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
    ).make()
    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.email],
    )

    with login(client):
        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert collaborator in project.members.all()


#####################################################################
# Advisor ACLs
#####################################################################


@pytest.mark.django_db
def test_collaborator_cannot_remove_advisor_from_project(request, client):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.email],
    )

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders.all()


@pytest.mark.django_db
def test_advisor_cannot_remove_advisor_from_project(request, client):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.email],
    )

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders.all()


@pytest.mark.django_db
def test_staff_can_remove_advisor_from_project_on_site(request, client):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )
    project = Recipe(
        models.Project,
        sites=[site],
        status="READY",
    ).make()
    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.email],
    )

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    assert (
        models.ProjectSwitchtender.objects.filter(
            project=project, site=site, switchtender=advisor
        ).count()
        == 0
    )


########################################################################
# resend invitations
########################################################################


@pytest.mark.django_db
def test_staff_can_resend_advisor_invitation(request, client, mocker):
    site = get_current_site(request)
    invited = baker.make(
        auth_models.User,
        username="invited@party.com",
        email="invited@party.com",
    )
    inviter = baker.make(
        auth_models.User,
        username="inviter@example.com",
        email="inviter@example.com",
    )
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="SWITCHTENDER",
        email=invited.username,
        inviter=inviter,
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_email")

    url = reverse(
        "projects-project-access-advisor-resend-invite",
        args=[project.id, invite.pk],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    communication_api.send_email.assert_called_once()


@pytest.mark.django_db
def test_staff_can_resend_collaborator_invitation(request, client, mocker):
    site = get_current_site(request)
    invited = baker.make(
        auth_models.User,
        username="invited@party.com",
        email="invited@party.com",
    )
    inviter = baker.make(
        auth_models.User,
        username="inviter@example.com",
        email="inviter@example.com",
    )
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="COLLABORATOR",
        email=invited.username,
        inviter=inviter,
    )

    mocker.patch("urbanvitaliz.apps.communication.api.send_email")

    url = reverse(
        "projects-project-access-collectivity-resend-invite",
        args=[project.id, invite.pk],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    communication_api.send_email.assert_called_once()


# eof
