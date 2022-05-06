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
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz.apps.communication import models as communication
from urbanvitaliz.apps.geomatics import models as geomatics
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


########################################################################
# Onboarding page
########################################################################


def test_onboarding_page_is_reachable_without_login(client):
    url = reverse("projects-onboarding")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-onboarding"')


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_project(client):
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }
    response = client.post(reverse("projects-onboarding"), data=data)
    project = models.Project.objects.all()[0]
    assert project.name == "a project"
    assert project.status == "DRAFT"
    assert len(project.ro_key) == 32
    assert data["email"] in project.emails
    note = models.Note.objects.all()[0]
    assert note.project == project
    assert note.public
    assert note.content == f"# Demande initiale\n\n{project.impediments}"
    assert response.status_code == 302


@pytest.mark.django_db
def test_performing_onboarding_create_a_new_user_and_logs_in(client):
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }
    response = client.post(reverse("projects-onboarding"), data=data)
    project = models.Project.fetch()[0]
    user = auth.User.objects.get(username=project.email)

    assert user.first_name == data["first_name"]
    assert user.last_name == data["last_name"]

    assert user.is_authenticated
    url = reverse("survey-project-session", args=[project.id])
    assert response.status_code == 302
    assert response.url == (url + "?first_time=1")


@pytest.mark.django_db
def test_performing_onboarding_sends_notification_to_project_moderators(client):
    md_group = Recipe(auth.Group, name="project_moderator").make()
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    moderator = Recipe(
        auth.User, email="moderator@example.com", groups=[md_group, st_group]
    ).make()

    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "first_name": "john",
        "last_name": "doe",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }

    client.post(reverse("projects-onboarding"), data=data)

    assert moderator.notifications.count() == 1


@pytest.mark.django_db
def test_performing_onboarding_sets_existing_postal_code(client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "postcode": commune.postal,
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )
    assert response.status_code == 302
    project = models.Project.on_site.all()[0]
    assert project.commune == commune


@pytest.mark.django_db
def test_performing_onboarding_discard_unknown_postal_code(client):
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "postcode": "12345",
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

    assert response.status_code == 302
    project = models.Project.on_site.all()[0]
    assert project.commune is None


@pytest.mark.django_db
def test_performing_onboarding_allow_select_on_multiple_communes(client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    Recipe(geomatics.Commune, postal="12345").make()
    with login(client):
        response = client.post(
            reverse("projects-onboarding"),
            data={
                "name": "a project",
                "email": "a@example.com",
                "location": "some place",
                "first_name": "john",
                "last_name": "doe",
                "postcode": commune.postal,
                "impediment_kinds": ["Autre"],
                "impediments": "some impediment",
            },
        )

    assert response.status_code == 302
    project = models.Project.fetch()[0]
    url = reverse("projects-onboarding-select-commune", args=[project.id])
    assert response.url == (url)


@pytest.mark.django_db
def test_selecting_proper_commune_completes_project_creation(request, client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    selected = Recipe(geomatics.Commune, postal="12345").make()
    with login(client) as user:
        project = Recipe(
            models.Project,
            sites=[get_current_site(request)],
            email=user.email,
            commune=commune,
        ).make()
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

    with login(client) as user:
        project = Recipe(
            models.Project,
            sites=[get_current_site(request)],
            email=user.email,
            commune=expected[1],
        ).make()
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
def test_create_prefilled_project_is_not_reachable_without_login(client):
    url = reverse("projects-project-prefill")
    response = client.get(url)
    assert response.status_code == 403


def test_create_prefilled_project_is_not_reachable_with_simple_login(client):
    with login(client):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 403


def test_create_prefilled_project_reachable_by_switchtenders(client):
    with login(client, groups=["switchtender"]):
        response = client.get(reverse("projects-project-prefill"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_create_prefilled_project_creates_a_new_project(client):
    data = {
        "name": "a project",
        "email": "a@example.com",
        "location": "some place",
        "postal": "59000",
        "first_name": "john",
        "last_name": "doe",
        "impediment_kinds": ["Autre"],
        "impediments": "some impediment",
    }
    with login(client, groups=["switchtender"]):
        response = client.post(reverse("projects-project-prefill"), data=data)

    project = models.Project.on_site.all()[0]
    assert project.name == "a project"
    assert project.status == "TO_PROCESS"
    assert len(project.ro_key) == 32
    assert data["email"] in project.emails

    assert response.status_code == 302


########################################################################
# My projects
########################################################################


@pytest.mark.django_db
def test_my_projects_are_stored_in_session_on_login(request, client):
    project = Recipe(
        models.Project, sites=[get_current_site(request)], email="my@example.com"
    ).make()
    with login(client, is_staff=False, email="my@example.com"):
        pass

    assert len(client.session["projects"]) == 1
    session_project = client.session["projects"][0]
    assert session_project["id"] == project.id


@pytest.mark.django_db
def test_other_projects_are_not_stored_in_session(client):
    project = Recipe(models.Project, email="other@exmaple.com").make()
    with login(client, is_staff=False):
        pass
    assert {"name": project.name, "id": project.id} not in client.session["projects"]


######
# Sharing link
######
@pytest.mark.django_db
def test_project_access_proper_sharing_link(client):
    project = Recipe(models.Project).make()
    url = reverse(
        "projects-project-sharing-link", kwargs={"project_ro_key": project.ro_key}
    )
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_project_fails_unknown_sharing_link(client):
    Recipe(models.Project).make()
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
    # project email is same as test user to be logged in
    with login(client, is_staff=False) as user:
        project = Recipe(
            models.Project, sites=[get_current_site(request)], email=user.email
        ).make()
        url = reverse("projects-project-detail-knowledge", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_switchtender(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_restricted_switchtender(request, client):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
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
    with login(client, is_staff=False) as user:
        project = Recipe(
            models.Project, sites=[get_current_site(request)], email=user.email
        ).make()
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
    # project email is same as test user to be logged in
    with login(client, is_staff=False) as user:
        project = Recipe(
            models.Project, sites=[get_current_site(request)], email=user.email
        ).make()
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
    with login(client, is_staff=False) as user:
        project = Recipe(
            models.Project, sites=[get_current_site(request)], email=user.email
        ).make()
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
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
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
        project.switchtenders.add(user)
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
        project.switchtenders.add(user)
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
        project.switchtenders.add(user)
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
        project.switchtenders.add(user)
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

    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune=commune,
        email=regional_actor.email,
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

    non_regional_actor = Recipe(auth.User, email="somewhere@else.info").make()
    non_regional_actor.groups.add(group)
    non_regional_actor.profile.departments.add(dpt_pdc)

    owner = Recipe(auth.User, email="here@project.info").make()
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        commune=commune,
        email=owner.email,
    ).make()

    with login(client, groups=["switchtender"]):
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
def test_general_notifications_are_consumed_on_project_knowledge(request, client):

    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
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

        url = reverse("projects-project-detail-knowledge", args=[project.id])

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
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="DRAFT",
        emails=[user.email],
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

    assert user.notifications.unsent().count() == 0


def test_notification_not_sent_when_project_is_muted(request):
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        status="READY",
        muted=True,
        emails=[user.email],
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

    assert user.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_non_staff_cannot_add_email_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-access-update", args=[project.id])

    with login(client, is_staff=False):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_add_email_to_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "test@example.com", "role": "COLLABORATOR"}

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        client.post(url, data=data)

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_can_add_email_to_project_if_not_draft(request, client):
    email = "owner@example.com"
    project = Recipe(
        models.Project, sites=[get_current_site(request)], email=email, status="READY"
    ).make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com", "role": "COLLABORATOR"}

    with login(client, email=email, is_staff=False):
        client.post(url, data=data)

    invite = invites_models.Invite.on_site.first()
    assert invite.email == data["email"]


@pytest.mark.django_db
def test_owner_cannot_add_email_to_project_if_draft(request, client):
    email = "owner@example.com"
    project = Recipe(
        models.Project, sites=[get_current_site(request)], email=email, status="DRAFT"
    ).make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, email=email, is_staff=False):
        response = client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_non_staff_cannot_delete_email_from_project(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-access-delete", args=[project.id, "test@example.com"])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_can_remove_email_from_project_if_not_draft(request, client):
    email = "owner@example.com"
    colab_email = "collaborator@example.com"
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        email=email,
        emails=[email, colab_email],
        status="READY",
    ).make()
    url = reverse(
        "projects-access-delete",
        args=[project.id, colab_email],
    )

    with login(client, email=email, is_staff=False):
        client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert colab_email not in project.emails


@pytest.mark.django_db
def test_owner_cannot_remove_email_from_project_if_draft(request, client):
    email = "owner@example.com"
    colab_email = "collaborator@example.com"
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
        email=email,
        emails=[email, colab_email],
        status="DRAFT",
    ).make()
    url = reverse("projects-access-delete", args=[project.id, colab_email])

    with login(client, email=email, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_delete_email_from_project(request, client):
    email = "test@example.com"
    project = Recipe(
        models.Project, sites=[get_current_site(request)], emails=[email]
    ).make()
    url = reverse("projects-access-delete", args=[project.id, email])

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert email not in project.emails

    update_url = reverse("projects-access-update", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(request, client):
    email = "test@example.com"
    project = Recipe(
        models.Project, sites=[get_current_site(request)], email=email, emails=[email]
    ).make()
    url = reverse("projects-access-delete", args=[project.id, email])

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert email in project.emails

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
    project = Recipe(
        models.Project, sites=[get_current_site(request)], email="owner@example.com"
    ).make()
    task = Recipe(models.Task, site=get_current_site(request), project=project).make()
    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}
    with login(client, email=project.email):
        response = client.post(url, data=data)
    assert response.status_code == 302
    reminder = reminders.Mail.to_send.all()[0]
    assert models.TaskFollowupRsvp.objects.count() == 1
    assert reminder.recipient == project.email
    in_fifteen_days = datetime.date.today() + datetime.timedelta(days=data["days"])
    assert reminder.deadline == in_fifteen_days


@pytest.mark.django_db
def test_create_reminder_without_delay_for_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
    task = Recipe(
        models.Task, site=get_current_site(request), project__email="owner@example.com"
    ).make()
    url = reverse("projects-remind-task", args=[task.id])
    with login(client, email=task.project.email):
        response = client.post(url)
    assert response.status_code == 302
    assert reminders.Mail.to_send.count() == 1
    assert models.TaskFollowupRsvp.objects.count() == 1


@pytest.mark.django_db
def test_recreate_reminder_after_for_same_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
    task = Recipe(
        models.Task, site=get_current_site(request), project__email="owner@example.com"
    ).make()
    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}
    data2 = {"days": 10}
    with login(client, email=task.project.email):
        response = client.post(url, data=data)
        response = client.post(url, data=data2)

    assert response.status_code == 302
    reminder = reminders.Mail.to_send.all()[0]
    assert reminders.Mail.to_send.count() == 1
    in_ten_days = datetime.date.today() + datetime.timedelta(days=data2["days"])
    assert reminder.deadline == in_ten_days
    assert models.TaskFollowupRsvp.objects.count() == 1


@pytest.mark.django_db
def test_recreate_reminder_before_for_same_task(request, client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
    task = Recipe(
        models.Task, site=get_current_site(request), project__email="owner@example.com"
    ).make()
    url = reverse("projects-remind-task", args=[task.id])
    data = {"days": 5}
    data2 = {"days": 2}
    with login(client, email=task.project.email):
        response = client.post(url, data=data)
        response = client.post(url, data=data2)

    assert response.status_code == 302
    assert reminders.Mail.to_send.count() == 1
    reminder = reminders.Mail.to_send.all()[0]
    in_two_days = datetime.date.today() + datetime.timedelta(days=data2["days"])
    assert reminder.deadline == in_two_days
    assert models.TaskFollowupRsvp.objects.count() == 1


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
    with login(client) as user:
        project = baker.make(
            models.Project,
            sites=[get_current_site(request)],
            status="READY",
            email=user.email,
        )
        task = baker.make(models.Task, site=get_current_site(request), project=project)
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)
    followup = models.TaskFollowup.objects.all()[0]
    assert followup.task == task
    assert followup.status == 0  # to be replaced by task status
    assert followup.comment == data["comment"]
    assert followup.who == user


@pytest.mark.django_db
def test_followup_triggers_notifications(request, client):
    group = auth.Group.objects.get(name="switchtender")
    switchtender = baker.make(auth.User, groups=[group])

    collab = baker.make(auth.User, email="collab@example.com")

    data = dict(comment="some comment")

    owner = None
    with login(client) as user:
        owner = user
        project = baker.make(
            models.Project,
            status="READY",
            sites=[get_current_site(request)],
            email=user.email,
            emails=[user.email, collab.email],
            switchtenders=[switchtender],
        )
        task = baker.make(models.Task, site=get_current_site(request), project=project)
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)

    assert switchtender.notifications.unread().count() == 1
    assert collab.notifications.unread().count() == 1
    assert owner.notifications.unread().count() == 0


@pytest.mark.django_db
def test_user_is_redirected_after_followup_on_task(request, client):
    with login(client) as user:
        project = baker.make(
            models.Project,
            sites=[get_current_site(request)],
            status="READY",
            email=user.email,
        )
        task = baker.make(models.Task, site=get_current_site(request), project=project)
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

    user = baker.make(auth.User, email="owner@example.com")
    project = baker.make(models.Project, status="READY", email=user.email)
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

    user = baker.make(auth.User, email="owner@example.com")
    project = baker.make(models.Project, status="READY", email=user.email)
    task = baker.make(models.Task, project=project)
    rsvp = baker.make(models.TaskFollowupRsvp, task=task, user=user)
    url = reverse("projects-rsvp-followup-task", args=[rsvp.uuid, status])
    client.post(url, data=data)

    assert models.TaskFollowupRsvp.objects.filter(uuid=rsvp.uuid).count() == 0
    followup = models.TaskFollowup.objects.all()[0]
    assert followup.task == task
    assert followup.status == status
    assert followup.comment == data["comment"]
    assert followup.who == user


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
        project.switchtenders.add(user)
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
    assert project.switchtenders.count() == 1
    assert project.switchtenders.first() == user


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
        project.switchtenders.add(user)
        assert project.switchtenders.count() == 1

        # Then POST to leave projet
        response = client.post(url)

    project = models.Project.on_site.get(pk=project.pk)

    assert response.status_code == 302
    assert project.switchtenders.count() == 0


@pytest.mark.django_db
def test_switchtender_joins_and_leaves_on_the_same_12h_should_not_notify(client):
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    collab = Recipe(auth.User, username="collab", email="collab@example.com").make()

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
        email=collab.email,
        emails=[collab.email],
        commune=commune,
    ).make()

    join_url = reverse("projects-project-switchtender-join", args=[project.id])
    leave_url = reverse("projects-project-switchtender-leave", args=[project.id])
    with login(client, groups=["switchtender"]):
        client.post(join_url)
        assert collab.notifications.count() == 1

        client.post(leave_url)

        assert collab.notifications.count() == 0


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
        p1.switchtenders.add(user)

        response = client.get(url)

    assert response.status_code == 200

    content = response.content.decode("utf-8")
    cvs_reader = csv.reader(io.StringIO(content))
    body = list(cvs_reader)
    body.pop(0)

    assert len(body) == 1


# eof
