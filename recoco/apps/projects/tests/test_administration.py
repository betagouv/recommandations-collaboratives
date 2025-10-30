# encoding: utf-8

"""
Tests for project application / administration

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2022-12-26 11:54:56 CEST
"""

from datetime import datetime

import pytest
from actstream.models import action_object_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications.signals import notify
from pytest_django.asserts import assertContains, assertRedirects

from recoco import verbs
from recoco.apps.communication import api as communication_api
from recoco.apps.geomatics import models as geomatics
from recoco.apps.invites import models as invites_models
from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import assign_advisor, assign_collaborator
from recoco.utils import login

from .. import models

########################################################################
# Project administration
########################################################################


@pytest.mark.django_db
def test_project_admin_not_available_for_unprivileged_users(request, client, project):
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

    actions = action_object_stream(project)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Project.EDITED
    assert "nom" in actions[0].description
    assert "adresse" in actions[0].description
    assert "contexte" in actions[0].description
    assert "code postal" not in actions[0].description
    assert "commune" not in actions[0].description


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

    actions = action_object_stream(project)
    assert actions.count() == 1
    assert actions[0].verb == verbs.Project.EDITED
    assert "nom" in actions[0].description
    assert "adresse" in actions[0].description
    assert "contexte" in actions[0].description
    assert "code postal" in actions[0].description
    assert "commune" in actions[0].description


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
def test_draft_project_update_not_accessible_for_collaborator(
    request, client, project_draft
):
    commune = Recipe(geomatics.Commune, postal="12345").make()

    project_draft.commune = commune
    project_draft.save()

    url = reverse("projects-project-administration", args=[project_draft.id])

    with login(client) as user:
        assign_collaborator(user, project_draft)
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_accepted_project_update_accessible_for_collaborator(request, client, project):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project.commune = commune
    project.save()

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
def test_promote_referent_not_available_for_unprivileged_users(
    request, client, project
):
    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(project.sites.first())

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
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_promote_referent_available_for_advisor(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    crm_user = baker.make(auth_models.User)
    profile = crm_user.profile
    profile.sites.add(site)
    profile.phone_no = "555-1234"
    profile.save()

    powner = baker.make(projects_models.ProjectMember, project=project, is_owner=False)
    pmember = baker.make(
        projects_models.ProjectMember, project=project, member=crm_user, is_owner=False
    )

    url = reverse("projects-project-promote-referent", args=[project.id, crm_user.id])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    powner.refresh_from_db()
    assert powner.is_owner is False
    pmember.refresh_from_db()
    assert pmember.is_owner is True

    # project phone number is updated to current owner one's
    project.refresh_from_db()
    assert project.phone == pmember.member.profile.phone_no


#####################################################################
# Removing collaborators from project
#####################################################################


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(request, client, project):
    site = get_current_site(request)

    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project.projectmember_set.add(membership)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, membership.member.username],
    )

    with login(client) as user:
        assign_advisor(user, project, site=site)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert membership in project.projectmember_set.all()

    update_url = reverse("projects-project-administration", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_collaborator_can_remove_other_collaborator_from_project(
    request, client, project
):
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )
    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.username],
    )

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url)

    assert response.status_code == 302
    assert "login" not in response.url  # not a simple redirect to login

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.projectmember_set.all()


@pytest.mark.django_db
def test_collaborator_can_remove_herself_project(request, client, project):
    with login(client) as user:
        assign_collaborator(user, project, is_owner=False)
        url = reverse(
            "projects-project-access-collectivity-delete",
            args=[project.id, user.username],
        )

        response = client.post(url)

    assert response.status_code == 302
    assert "login" not in response.url  # not a simple redirect to login

    project = models.Project.on_site.get(id=project.id)
    assert user not in project.projectmember_set.all()


@pytest.mark.django_db
def test_advisor_can_remove_collaborator_from_project(request, client, project):
    site = get_current_site(request)
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )

    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.username],
    )

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.members.all()


@pytest.mark.django_db
def test_unassigning_a_collaborator_cleans_notifications(request, client, project):
    site = get_current_site(request)
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )

    assign_collaborator(collaborator, project)

    notify.send(
        sender=collaborator,
        actor=collaborator,
        recipient=collaborator,
        verb="noop",
        target=project,
    )

    assert collaborator.notifications.count() == 1

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.username],
    )

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 302

    assert collaborator.notifications.count() == 0


@pytest.mark.django_db
def test_staff_can_remove_collaborator_from_project(request, client, project):
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )

    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.username],
    )

    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert collaborator not in project.members.all()


@pytest.mark.django_db
def test_unprivileged_user_cannot_remove_collaborator_from_project(
    request, client, project
):
    collaborator = baker.make(
        auth_models.User,
        email="owner@ab.fr",
        username="owner@ab.fr",
    )

    assign_collaborator(collaborator, project)

    url = reverse(
        "projects-project-access-collectivity-delete",
        args=[project.id, collaborator.username],
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
def test_collaborator_cannot_remove_advisor_from_project(request, client, project):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )

    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.username],
    )

    with login(client) as user:
        assign_collaborator(user, project)
        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders.all()


@pytest.mark.django_db
def test_advisor_cannot_remove_advisor_from_project(request, client, project):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )

    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.username],
    )

    with login(client) as user:
        assign_advisor(user, project, site)
        response = client.post(url)

    assert response.status_code == 403

    project = models.Project.on_site.get(id=project.id)
    assert advisor in project.switchtenders.all()


@pytest.mark.django_db
def test_advisor_can_remove_herself_from_project(request, client, project):
    site = get_current_site(request)

    with login(client) as user:
        assign_advisor(user, project, site)
        url = reverse(
            "projects-project-access-advisor-delete",
            args=[project.id, user.username],
        )

        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert user not in project.switchtenders.all()


@pytest.mark.django_db
def test_removing_advisor_cleans_notifications(request, client, project):
    site = get_current_site(request)

    with login(client) as user:
        assign_advisor(user, project, site)

        notify.send(
            sender=user,
            actor=user,
            recipient=user,
            verb="noop",
            target=project,
        )

        assert user.notifications.count() == 1

        url = reverse(
            "projects-project-access-advisor-delete",
            args=[project.id, user.username],
        )

        response = client.post(url)

    assert response.status_code == 302
    assert user.notifications.count() == 0


@pytest.mark.django_db
def test_removing_advisor_cleans_dashboard_entries(request, client, project):
    site = get_current_site(request)

    with login(client) as user:
        assign_advisor(user, project, site)

        models.UserProjectStatus.objects.get_or_create(
            site=site,
            user=user,
            project=project,
            defaults={"status": "TODO"},
        )

        url = reverse(
            "projects-project-access-advisor-delete",
            args=[project.id, user.username],
        )

        response = client.post(url)

    assert response.status_code == 302
    assert models.UserProjectStatus.objects.count() == 0


@pytest.mark.django_db
def test_staff_can_remove_advisor_from_project_on_site(request, client, project):
    site = get_current_site(request)
    advisor = baker.make(
        auth_models.User,
        email="advisor@ab.fr",
        username="advisor@ab.fr",
    )

    assign_advisor(advisor, project, site)

    url = reverse(
        "projects-project-access-advisor-delete",
        args=[project.id, advisor.username],
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
def test_staff_can_resend_advisor_invitation(request, client, project, mocker):
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

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="SWITCHTENDER",
        email=invited.username,
        inviter=inviter,
    )

    mocker.patch("recoco.apps.communication.api.send_email")

    url = reverse(
        "projects-project-access-advisor-resend-invite",
        args=[project.id, invite.pk],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    communication_api.send_email.assert_called_once()


@pytest.mark.django_db
def test_staff_can_resend_collaborator_invitation(request, client, mocker, project):
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

    invite = baker.make(
        invites_models.Invite,
        site=site,
        project=project,
        role="COLLABORATOR",
        email=invited.username,
        inviter=inviter,
    )

    mocker.patch("recoco.apps.communication.api.send_email")

    url = reverse(
        "projects-project-access-collectivity-resend-invite",
        args=[project.id, invite.pk],
    )
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    assert response.status_code == 302

    communication_api.send_email.assert_called_once()


@pytest.mark.django_db
def test_set_project_active_date_is_saved(client, project_ready, current_site):
    project_ready.inactive_since = datetime(2024, 1, 1)
    project_ready.save()

    date = datetime(2024, 1, 16)
    url = reverse("projects-project-set-active", args=[project_ready.id])
    with login(client, is_staff=True, groups=["example_com_staff"]):
        with freeze_time("2024-01-16"):
            client.post(url)

    project_ready.refresh_from_db()
    assert project_ready.last_manual_reactivation.astimezone() == date.astimezone()
    assert project_ready.inactive_since is None
    assert project_ready.inactive_reason is None


# eof
