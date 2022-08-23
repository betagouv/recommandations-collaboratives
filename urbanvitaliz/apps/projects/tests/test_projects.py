# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import csv
import datetime
import io
import uuid

import django.core.mail
import pytest
from django.contrib.auth import models as auth
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import notify
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertRedirects)
from urbanvitaliz.apps.communication import models as communication
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.invites import models as invites_models
from urbanvitaliz.apps.reminders import models as reminders
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.utils import login

from .. import models, signals

# TODO when local authority can see & update her project
# TODO check that project, note, and task belong to her


########################################################################
# Landing page
########################################################################


def test_home_page_is_reachable_without_login(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, "UrbanVitaliz")


@pytest.mark.django_db
def test_selecting_proper_commune_completes_project_creation(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    selected = Recipe(geomatics.Commune, postal="12345").make()
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        commune=commune,
    ).make()

    with login(client, user=membership.member):
        response = client.post(
            reverse("projects-onboarding-select-commune", args=[project.id]),
            data={"commune": selected.id},
        )
    project = models.Project.on_site.get(id=project.id)
    assert project.commune == selected
    assert response.status_code == 302
    expected = reverse("survey-project-session", args=[project.id]) + "?first_time=1"
    assert response.url == expected


@pytest.mark.django_db
def test_proper_commune_selection_contains_all_possible_commmunes(request, client):
    expected = [
        Recipe(geomatics.Commune, postal="12345").make(),
        Recipe(geomatics.Commune, postal="12345").make(),
    ]
    unexpected = Recipe(geomatics.Commune, postal="67890").make()

    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        commune=expected[1],
    ).make()

    with login(client, user=membership.member):
        response = client.get(
            reverse("projects-onboarding-select-commune", args=[project.id]),
        )
    page = str(response.content)
    for commune in expected:
        assert commune.name in page
    assert unexpected.name not in page


#################################################################
# Prefilled projects
#################################################################
def test_create_prefilled_project_is_not_reachable_without_login(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    url = reverse("projects-project-prefill")
    response = client.get(url)
    assert response.status_code == 403


def test_create_prefilled_project_is_not_reachable_with_simple_login(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    with login(client):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 403


def test_create_prefilled_project_reachable_by_switchtenders(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    with login(client, groups=["switchtender"]):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_prefilled_project_creates_a_new_project(request, client):
    baker.make(home_models.SiteConfiguration, site=get_current_site(request))

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "phone": "03939382828",
        "postcode": "59000",
        "org_name": "my org",
        "description": "blah",
        "first_name": "john",
        "last_name": "doe",
        "response_0": "blah",
    }
    with login(client, groups=["switchtender"]):
        response = client.post(reverse("projects-project-prefill"), data=data)

    project = models.Project.on_site.all()[0]
    assert project.name == "a project"
    assert project.status == "TO_PROCESS"
    assert len(project.ro_key) == 32

    assert data["email"] in [member.email for member in project.members.all()]

    assert response.status_code == 302


########################################################################
# My projects
########################################################################


@pytest.mark.django_db
def test_my_projects_are_stored_in_session_on_login(request, client):
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    ).make()
    with login(client, user=membership.member):
        pass

    assert len(client.session["projects"]) == 1
    session_project = client.session["projects"][0]
    assert session_project["id"] == project.id


@pytest.mark.django_db
def test_other_projects_are_not_stored_in_session(client):
    membership = baker.make(models.ProjectMember, is_owner=True)
    project = Recipe(models.Project, projectmember_set=[membership]).make()
    with login(client, user=membership.member):
        pass
    assert {"name": project.name, "id": project.id} not in client.session["projects"]


######
# Sharing link
######
@pytest.mark.django_db
def test_project_access_proper_sharing_link(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse(
        "projects-project-sharing-link", kwargs={"project_ro_key": project.ro_key}
    )
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_project_fails_unknown_sharing_link(request, client):
    current_site = get_current_site(request)
    Recipe(models.Project, sites=[current_site]).make()
    url = reverse("projects-project-sharing-link", kwargs={"project_ro_key": "unkown"})
    response = client.get(url)
    assert response.status_code == 404


########################################################################
# login
########################################################################


@pytest.mark.django_db
def test_existing_user_receives_email_on_login(client):
    user = Recipe(auth.User, email="jdoe@example.com").make()
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": user.email})
    assert response.status_code == 302
    assert len(django.core.mail.outbox) == 1
    assert user.email in django.core.mail.outbox[0].to


@pytest.mark.django_db
def test_unknown_user_is_created_and_receives_email_on_login(client):
    email = "jdoe@example.com"
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": email})
    assert response.status_code == 302
    assert auth.User.objects.get(email=email)
    assert len(django.core.mail.outbox) == 1
    assert email in django.core.mail.outbox[0].to


########################################################################
# List of projects
########################################################################


@pytest.mark.django_db
def test_project_list_not_available_for_non_staff_users(client):
    url = reverse("projects-project-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_list_available_for_switchtender_user(client):
    url = reverse("projects-project-list")
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_excludes_project_not_in_switchtender_departments(request, client):
    department = Recipe(geomatics.Department, code="00").make()
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    ).make()
    url = reverse("projects-project-list")
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(department)
        response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertNotContains(response, detail_url)


########################################################################
# Project details
########################################################################

# Overview
@pytest.mark.django_db
def test_project_overview_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-overview", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_overview_available_for_owner(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project, sites=[current_site], projectmember_set=[membership]
    ).make()

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-project-detail-overview", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_overview_available_for_switchtender(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse("projects-project-detail-overview", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


# Knowledge
@pytest.mark.django_db
def test_project_knowledge_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_knowledge_available_for_owner(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project, sites=[current_site], projectmember_set=[membership]
    ).make()

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-project-detail-knowledge", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_switchtender(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_restricted_switchtender(request, client):
    current_site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=current_site)

    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        sites=[current_site],
        commune__departments__code="01",
    ).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 200


# actions
@pytest.mark.django_db
def test_project_actions_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_actions_available_for_owner(request, client):
    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    ).make()

    with login(client, user=membership.member, is_staff=False):
        url = reverse("projects-project-detail-actions", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_actions_available_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_actions_available_for_restricted_switchtender(request, client):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[get_current_site(request)],
    ).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 200


# conversations
@pytest.mark.django_db
def test_project_conversations_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_conversations_available_for_owner(request, client):
    membership = baker.make(models.ProjectMember, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    ).make()

    with login(client, user=membership.member):
        url = reverse("projects-project-detail-conversations", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_conversations_available_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_conversations_available_for_restricted_switchtender(request, client):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[get_current_site(request)],
    ).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 200


# internal
@pytest.mark.django_db
def test_project_internal_followup_not_available_for_non_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-internal-followup", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_not_available_for_owner(request, client):
    # project email is same as test user to be logged in
    membership = baker.make(models.ProjectMember, member__is_staff=False, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    ).make()

    with login(client, user=membership.member):
        url = reverse("projects-project-detail-internal-followup", args=[project.id])
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_available_for_assigned_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-internal-followup", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_not_available_for_restricted_switchtender(
    request, client
):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[get_current_site(request)],
    ).make()
    url = reverse("projects-project-detail-internal-followup", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_contains_informations(request, client):
    current_site = get_current_site(request)
    Recipe(home_models.SiteConfiguration, site=current_site).make()
    project = Recipe(models.Project, sites=[current_site]).make()
    task = Recipe(models.Task, project=project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assertContains(response, project.description)
    assertContains(response, task.content)
    assertContains(response, note.content)


@pytest.mark.django_db
def test_project_detail_contains_actions_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)
    add_task_url = reverse("projects-project-create-action", args=[project.id])
    assertContains(response, add_task_url)


########################################################################
# update project
########################################################################


@pytest.mark.django_db
def test_update_project_not_available_for_non_staff_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_project_available_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_project_wo_commune_and_redirect(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-update", args=[project.id])
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "description": "a project description",
        "impediment": "some impediment",
    }

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    project = models.Project.on_site.get(id=project.id)
    assert project.name == data["name"]
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_update_project_with_commune(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=commune
    ).make()
    url = reverse("projects-project-update", args=[project.id])

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)

    assertContains(response, "<form")
    assertContains(response, commune.postal)


########################################################################
# accept project
########################################################################


@pytest.mark.django_db
def test_accept_project_not_available_for_non_staff_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-accept", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_accept_project_and_redirect(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    Recipe(auth.Group, name="project_moderator").make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, groups=["project_moderator", "switchtender"]):
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert project.status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_accept_project_notifies_regional_actors(request, client):
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    auth.Group.objects.get_or_create(name="project_moderator")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)

    membership = baker.make(models.ProjectMember, member=regional_actor, is_owner=True)

    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune=commune,
        projectmember_set=[membership],
    ).make()

    with login(client, groups=["switchtender", "project_moderator"]):
        client.post(reverse("projects-project-accept", args=[project.id]))

    assert regional_actor.notifications.count() == 1


@pytest.mark.django_db
def test_accept_project_does_not_notify_non_regional_actors(request, client):
    group = auth.Group.objects.get(name="switchtender")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    dpt_pdc = Recipe(geomatics.Department, code=62, name="Pas de Calais").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    non_regional_actor = baker.make(auth.User, email="somewhere@else.info")
    non_regional_actor.groups.add(group)
    non_regional_actor.profile.departments.add(dpt_pdc)

    nr_membership = baker.make(
        models.ProjectMember,
        member=non_regional_actor,
    )

    owner_membership = baker.make(models.ProjectMember, is_owner=True)
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune=commune,
        projectmember_set=[owner_membership],
    ).make()

    with login(client, user=nr_membership.member, groups=["switchtender"]):
        client.post(reverse("projects-project-accept", args=[project.id]))

    assert non_regional_actor.notifications.count() == 0


########################################################################
# delete project
########################################################################


@pytest.mark.django_db
def test_delete_project_not_available_for_non_staff_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-delete", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_project_and_redirect(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-delete", args=[project.id])

    # delete needs staff, list projects needs switchtender
    with login(client, groups=["switchtender"], is_staff=True):
        response = client.post(url)

    project = models.Project.deleted_on_site.get(id=project.id)
    assert project.deleted
    assert project.updated_on > updated_on_before

    list_url = reverse("projects-project-list")
    assertRedirects(response, list_url)


@pytest.mark.django_db
def test_general_notifications_are_consumed_on_project_overview(request, client):
    current_site = get_current_site(request)
    Recipe(home_models.SiteConfiguration, site=current_site).make()
    project = Recipe(
        models.Project,
        sites=[current_site],
        name="Proj1",
        location="Somewhere",
    ).make()

    with login(client, groups=["switchtender"], is_staff=False, username="Bob") as user:
        notify.send(
            sender=user,
            recipient=user,
            verb="est devenu·e aiguilleur·se sur le projet",
            target=project,
        )

        notify.send(
            sender=project,
            recipient=user,
            verb="a été validé",
            target=project,
        )

        assert user.notifications.unread().count() == 2

        url = reverse("projects-project-detail-overview", args=[project.id])

        response = client.get(url)
        assert response.status_code == 200

        assert user.notifications.unread().count() == 0


@pytest.mark.django_db
def test_notifications_are_deleted_on_project_hard_delete(request):
    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    recipient = Recipe(auth.User).make()

    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

    notify.send(
        sender=user,
        recipient=recipient,
        verb="a reçu une notif",
        action_object=project,
        target=project,
    )

    assert recipient.notifications.count() == 1
    project.delete()
    assert recipient.notifications.count() == 0


########################################################################
# modify who can access the project
########################################################################


def test_notification_not_sent_when_project_is_draft(request):
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()

    membership = baker.make(
        models.ProjectMember, member__is_staff=False, is_owner=False
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="DRAFT",
        projectmember_set=[membership],
    )

    # Generate a notification
    signals.action_created.send(
        sender=test_notification_not_sent_when_project_is_draft,
        task=models.Task.objects.create(
            project=project,
            site=get_current_site(request),
            created_by=switchtender,
        ),
        project=project,
        user=switchtender,
    )

    assert membership.member.notifications.unsent().count() == 0


def test_notification_not_sent_when_project_is_muted(request):
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    membership = baker.make(
        models.ProjectMember, member__is_staff=False, is_owner=False
    )
    project = baker.make(
        models.Project,
        status="DRAFT",
        sites=[get_current_site(request)],
        muted=True,
        projectmember_set=[membership],
    )

    # Generate a notification
    signals.action_created.send(
        sender=test_notification_not_sent_when_project_is_draft,
        task=models.Task.on_site.create(
            project=project, site=get_current_site(request), created_by=switchtender
        ),
        project=project,
        user=switchtender,
    )

    assert membership.member.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_non_staff_cannot_add_email_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-access-update", args=[project.id])

    with login(client, is_staff=False):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_add_email_to_project(request, client):
    project = baker.make(
        models.Project, sites=[get_current_site(request)], projectmember_set=[]
    )

    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "test@example.com", "role": "COLLABORATOR"}

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url, data=data)

    assert response.status_code == 302
    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_can_add_email_to_project_if_not_draft(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="own@er.fr",
        member__username="own@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com", "role": "COLLABORATOR"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 302

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_email_cannot_be_added_twice(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="own@er.fr",
        member__username="own@er.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com", "role": "COLLABORATOR"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)
        assert response.status_code == 302

        response = client.post(url, data=data)
        assert response.status_code == 200

    assert invites_models.Invite.objects.count() == 1
    invite = invites_models.Invite.objects.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_cannot_add_email_to_project_if_draft(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="user@staff.fr",
        member__username="user@staff.fr",
    )
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="DRAFT",
    ).make()

    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_non_staff_cannot_delete_email_from_project(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="user@staff.fr",
        member__username="user@staff.fr",
    )
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    ).make()

    url = reverse("projects-access-delete", args=[project.id, membership.member.email])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_can_remove_email_from_project_if_not_draft(request, client):
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
        member__username="owner@ab.fr",
    )
    collab_membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="coll@ab.fr",
        member__username="coll@ab.fr",
    )
    project = Recipe(
        models.Project,
        projectmember_set=[owner_membership, collab_membership],
        sites=[get_current_site(request)],
        status="READY",
    ).make()

    url = reverse(
        "projects-access-delete",
        args=[project.id, collab_membership.member.email],
    )

    with login(client, user=owner_membership.member):
        client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert collab_membership.member not in project.members.all()


@pytest.mark.django_db
def test_owner_cannot_remove_email_from_project_if_draft(request, client):
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
    )
    collab_membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__email="coll@ab.fr",
    )
    project = Recipe(
        models.Project,
        projectmember_set=[owner_membership, collab_membership],
        sites=[get_current_site(request)],
        status="DRAFT",
    ).make()

    url = reverse(
        "projects-access-delete", args=[project.id, collab_membership.member.email]
    )

    with login(client, user=owner_membership.member):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_delete_email_from_project(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=False,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-access-delete", args=[project.id, membership.member.email])

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url)

    assert response.status_code == 302

    project = models.Project.on_site.get(id=project.id)
    assert membership not in project.projectmember_set.all()

    update_url = reverse("projects-access-update", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(request, client):
    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
        status="READY",
    )

    url = reverse("projects-access-delete", args=[project.id, membership.member.email])

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert membership in project.projectmember_set.all()

    update_url = reverse("projects-access-update", args=[project.id])
    assertRedirects(response, update_url)


########################################################################
# Project syndication feed
########################################################################


@pytest.mark.django_db
def test_projects_feed_available_for_all_users(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-feed")
    response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


#
# reminder


@pytest.mark.django_db
def test_create_reminder_for_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")

    membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__username="coll@ab.fr",
        member__email="coll@ab.fr",
    )
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        projectmember_set=[membership],
    )
    task = baker.make(models.Task, site=get_current_site(request), project=project)

    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}

    with login(client, user=membership.member):
        response = client.post(url, data=data)

    assert response.status_code == 302
    reminder = reminders.Reminder.to_send.all()[0]
    assert models.TaskFollowupRsvp.objects.count() == 0
    assert reminder.recipient == project.members.first().email
    in_fifteen_days = datetime.date.today() + datetime.timedelta(days=data["days"])
    assert reminder.deadline == in_fifteen_days


@pytest.mark.django_db
def test_create_reminder_without_delay_for_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
    owner_membership = baker.make(
        models.ProjectMember,
        is_owner=True,
        member__is_staff=False,
        member__email="owner@ab.fr",
        member__username="owner@ab.fr",
    )
    task = baker.make(
        models.Task,
        site=get_current_site(request),
        project__projectmember_set=[owner_membership],
    )

    url = reverse("projects-remind-task", args=[task.id])

    with login(client, user=owner_membership.member):
        response = client.post(url)

    assert response.status_code == 302
    assert reminders.Reminder.to_send.count() == 1
    assert models.TaskFollowupRsvp.objects.count() == 0


@pytest.mark.django_db
def test_recreate_reminder_after_for_same_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")

    membership = baker.make(models.ProjectMember, is_owner=True)
    task = Recipe(
        models.Task,
        site=get_current_site(request),
        project__projectmember_set=[membership],
    ).make()

    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}
    data2 = {"days": 10}
    with login(client, user=membership.member):
        response = client.post(url, data=data)
        response = client.post(url, data=data2)

    assert response.status_code == 302
    reminder = reminders.Reminder.to_send.all()[0]
    assert reminders.Reminder.to_send.count() == 1
    in_ten_days = datetime.date.today() + datetime.timedelta(days=data2["days"])
    assert reminder.deadline == in_ten_days
    assert models.TaskFollowupRsvp.objects.count() == 0


@pytest.mark.django_db
def test_recreate_reminder_before_for_same_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")

    membership = baker.make(models.ProjectMember, is_owner=True)
    task = Recipe(
        models.Task,
        site=get_current_site(request),
        project__projectmember_set=[membership],
    ).make()

    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}
    data2 = {"days": 2}
    with login(client, user=membership.member):
        response = client.post(url, data=data)
        response = client.post(url, data=data2)

    assert response.status_code == 302
    assert reminders.Reminder.to_send.count() == 1
    reminder = reminders.Reminder.to_send.all()[0]
    in_two_days = datetime.date.today() + datetime.timedelta(days=data2["days"])
    assert reminder.deadline == in_two_days
    assert models.TaskFollowupRsvp.objects.count() == 0


########################################################################
# task followup
########################################################################

#
# simple followup


@pytest.mark.django_db
def test_user_cannot_followup_on_non_existant_task(client):
    url = reverse("projects-followup-task", args=[0])
    with login(client):
        response = client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_user_cannot_followup_on_someone_else_task(request, client):
    task = baker.make(models.Task, site=get_current_site(request))
    with login(client):
        url = reverse("projects-followup-task", args=[task.id])
        response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_can_followup_on_personal_task(request, client):
    data = dict(comment="some comment")

    membership = baker.make(models.ProjectMember, is_owner=True)

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
        projectmember_set=[membership],
    )
    task = baker.make(models.Task, site=get_current_site(request), project=project)

    with login(client, user=membership.member) as user:
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)

    followup = models.TaskFollowup.objects.all()[0]
    assert followup.task == task
    assert followup.status is None
    assert followup.comment == data["comment"]
    assert followup.who == user


@pytest.mark.django_db
def test_followup_triggers_notifications(request, client):
    group = auth.Group.objects.get(name="switchtender")
    switchtender = baker.make(auth.User, groups=[group])

    owner_membership = baker.make(models.ProjectMember, is_owner=True)
    collab_membership = baker.make(models.ProjectMember, is_owner=False)

    data = dict(comment="some comment")

    with login(client, user=owner_membership.member):
        project = baker.make(
            models.Project,
            status="READY",
            sites=[get_current_site(request)],
            projectmember_set=[owner_membership, collab_membership],
        )
        project.switchtenders_on_site.create(
            switchtender=switchtender, site=get_current_site(request)
        )
        task = baker.make(models.Task, site=get_current_site(request), project=project)
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)

    assert switchtender.notifications.unread().count() == 1
    assert collab_membership.member.notifications.unread().count() == 1
    assert owner_membership.member.notifications.unread().count() == 0


@pytest.mark.django_db
def test_user_is_redirected_after_followup_on_task(request, client):
    membership = baker.make(models.ProjectMember, is_owner=True)

    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
        projectmember_set=[membership],
    )
    task = baker.make(models.Task, site=get_current_site(request), project=project)

    with login(client, user=membership.member):
        url = reverse("projects-followup-task", args=[task.id])
        response = client.post(url)

    assert response.status_code == 302
    assert response.url == reverse(
        "projects-project-detail-actions", args=[task.project.id]
    )


#
# rsvp followup


@pytest.mark.django_db
def test_user_cannot_followup_on_non_existant_rsvp(client):
    bad_uuid = uuid.uuid4()
    url = reverse(
        "projects-rsvp-followup-task", args=[bad_uuid, models.Task.INPROGRESS]
    )
    with login(client):
        response = client.post(url)
    assert response.status_code == 200
    assertContains(response, "pas valide")


@pytest.mark.django_db
def test_user_cannot_followup_on_rsvp_with_bad_status(client):
    rsvp = baker.make(models.TaskFollowupRsvp)
    with login(client):
        url = reverse("projects-rsvp-followup-task", args=[rsvp.uuid, 0])
        response = client.post(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_user_can_followup_on_rsvp_using_mail_link(client):
    status = models.Task.INPROGRESS

    membership = baker.make(models.ProjectMember)
    project = baker.make(models.Project, status="READY", projectmember_set=[membership])
    task = baker.make(models.Task, project=project)
    rsvp = baker.make(models.TaskFollowupRsvp, task=task)
    url = reverse("projects-rsvp-followup-task", args=[rsvp.uuid, status])

    response = client.get(url)

    assert response.status_code == 200
    assertContains(response, '<form id="form-rsvp-followup-confirm"')


@pytest.mark.django_db
def test_user_can_followup_on_rsvp(client):
    data = dict(comment="some comment")
    status = models.Task.INPROGRESS

    membership = baker.make(models.ProjectMember)
    project = baker.make(models.Project, status="READY", projectmember_set=[membership])
    task = baker.make(models.Task, project=project)
    rsvp = baker.make(models.TaskFollowupRsvp, task=task, user=membership.member)
    url = reverse("projects-rsvp-followup-task", args=[rsvp.uuid, status])
    client.post(url, data=data)

    assert models.TaskFollowupRsvp.objects.filter(uuid=rsvp.uuid).count() == 0
    followup = models.TaskFollowup.objects.all()[0]
    assert followup.task == task
    assert followup.status == status
    assert followup.comment == data["comment"]
    assert followup.who == membership.member


########################################################################
# pushing a resource to a project's owner
########################################################################


@pytest.mark.django_db
def test_switchtender_push_resource_to_project_fails_if_no_project_in_session(client):
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_switchtender_create_action_for_resource_push(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    resource = Recipe(
        resources.Resource, sites=[current_site], status=resources.Resource.PUBLISHED
    ).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        session = client.session
        session["active_project"] = project.id
        session.save()

        response = client.post(url)

    newurl = (
        reverse("projects-project-create-action", args=[project.id])
        + f"?resource={resource.id}"
    )
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_switchtender_joins_project(request, client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()
    Recipe(
        models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=commune
    ).make()

    url = reverse("projects-project-switchtender-join", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        # Then POST to join projet
        response = client.post(url)

    project = models.Project.on_site.get(pk=project.pk)

    assert response.status_code == 302
    assert project.switchtenders_on_site.count() == 1
    assert project.switchtenders_on_site.first().switchtender == user


@pytest.mark.django_db
def test_switchtender_leaves_project(request, client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()
    Recipe(
        models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(
        models.Project, sites=[get_current_site(request)], commune=commune
    ).make()

    url = reverse("projects-project-switchtender-leave", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        assert project.switchtenders_on_site.count() == 1

        # Then POST to leave projet
        response = client.post(url)

    project = models.Project.on_site.get(pk=project.pk)

    assert response.status_code == 302
    assert project.switchtenders.count() == 0


@pytest.mark.django_db
def test_switchtender_joins_and_leaves_on_the_same_12h_should_not_notify(client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    membership = baker.make(models.ProjectMember, is_owner=True)

    Recipe(
        models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(
        models.Project,
        status="BLAH",
        projectmember_set=[membership],
        commune=commune,
    ).make()

    join_url = reverse("projects-project-switchtender-join", args=[project.id])
    leave_url = reverse("projects-project-switchtender-leave", args=[project.id])
    with login(client, groups=["switchtender"]):
        client.post(join_url)
        assert membership.member.notifications.count() == 1

        client.post(leave_url)

        assert membership.member.notifications.count() == 0


#################################################################
# CSV
#################################################################


def test_switchtender_exports_csv(request, client):
    # Expected project
    p1 = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        name="Projet 1",
        status="READY",
    ).make()
    p1.commune = Recipe(geomatics.Commune).make()
    p1.save()

    # Project that should not appear
    Recipe(models.Project, name="Projet 2").make()

    url = reverse("projects-project-list-export-csv")
    with login(client, groups=["switchtender"]) as user:
        p1.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.get(url)

    assert response.status_code == 200

    content = response.content.decode("utf-8")
    cvs_reader = csv.reader(io.StringIO(content))
    body = list(cvs_reader)
    body.pop(0)

    assert len(body) == 1


#################################################################
# Synopsis
#################################################################
@pytest.mark.django_db
def test_switchtender_writes_synopsis_for_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders_on_site.create(
            switchtender=user, site=get_current_site(request)
        )

        response = client.post(
            reverse("projects-project-synopsis", args=[project.id]),
            data={"synopsis": "this is some content"},
        )

    assert response.status_code == 302
    project = models.Project.objects.all()[0]
    assert project.synopsis is not None
    assert project.synopsis_on is not None
    assert project.synopsis_by == user


# eof
