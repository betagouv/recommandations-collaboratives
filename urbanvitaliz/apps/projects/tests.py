# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import datetime
import uuid

import django.core.mail
import pytest
from django.contrib.auth import models as auth
from django.contrib.messages import get_messages
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertRedirects)
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.reminders import models as reminders
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import login

from . import models, utils, views
from .templatetags import projects_extra

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
    project = models.Project.fetch()[0]
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
    assert user.is_authenticated
    url = reverse("survey-project-session", args=[project.id])
    assert response.status_code == 302
    assert response.url == (url + "?first_time=1")


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
    project = models.Project.fetch()[0]
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
    project = models.Project.fetch()[0]
    assert project.commune is None


########################################################################
# My projects
########################################################################


@pytest.mark.django_db
def test_my_projects_are_stored_in_session_on_login(client):
    project = Recipe(models.Project, email="my@example.com").make()
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
def test_project_list_includes_project_for_global_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-list")
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


@pytest.mark.django_db
def test_project_list_includes_project_in_switchtender_departments(client):
    project = Recipe(models.Project, commune__department__code="01").make()
    url = reverse("projects-project-list")
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(project.commune.department)
        response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


@pytest.mark.django_db
def test_project_list_excludes_project_not_in_switchtender_departments(client):
    department = Recipe(geomatics.Department, code="00").make()
    project = Recipe(models.Project, commune__department__code="01").make()
    url = reverse("projects-project-list")
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(department)
        response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertNotContains(response, detail_url)


########################################################################
# Project details
########################################################################


@pytest.mark.django_db
def test_project_detail_not_available_for_non_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_available_for_owner(client):
    # project email is same as test user to be logged in
    with login(client, is_staff=False) as user:
        project = Recipe(models.Project, email=user.email).make()
        url = reverse("projects-project-detail", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_not_available_for_restricted_switchtender(client):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(models.Project, commune__departments__code="01").make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_contains_informations(client):
    project = Recipe(models.Project).make()
    task = Recipe(models.Task, project=project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assertContains(response, project.description)
    assertContains(response, task.content)
    assertContains(response, note.content)


@pytest.mark.django_db
def test_project_detail_contains_actions(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    add_task_url = reverse("projects-create-task", args=[project.id])
    assertContains(response, add_task_url)
    add_note_url = reverse("projects-create-note", args=[project.id])
    assertContains(response, add_note_url)


########################################################################
# update project
########################################################################


@pytest.mark.django_db
def test_update_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_project_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-update", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_update_project_wo_commune_and_redirect(client):
    project = Recipe(models.Project).make()
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

    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    project = models.Project.objects.get(id=project.id)
    assert project.name == data["name"]
    assert project.updated_on > updated_on_before

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, detail_url)


@pytest.mark.django_db
def test_update_project_with_commune(client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    project = Recipe(models.Project, commune=commune).make()
    url = reverse("projects-project-update", args=[project.id])

    with login(client, groups=["switchtender"]):
        response = client.get(url)

    assertContains(response, "<form")
    assertContains(response, commune.postal)


########################################################################
# accept project
########################################################################


@pytest.mark.django_db
def test_accept_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-accept", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_accept_project_and_redirect(client):
    project = Recipe(models.Project).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, groups=["switchtender"]):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert project.status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, detail_url)


########################################################################
# delete project
########################################################################


@pytest.mark.django_db
def test_delete_project_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-delete", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_project_and_redirect(client):
    project = Recipe(models.Project).make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-delete", args=[project.id])

    # delete needs staff, list projects needs switchtender
    with login(client, groups=["switchtender"], is_staff=True):
        response = client.post(url)

    project = models.Project.objects_deleted.get(id=project.id)
    assert project.deleted
    assert project.updated_on > updated_on_before

    list_url = reverse("projects-project-list")
    assertRedirects(response, list_url)


########################################################################
# modify who can access the project
########################################################################


@pytest.mark.django_db
def test_contributor_has_the_same_rights_as_the_owner(client):
    owner = Recipe(auth.User, username="owner", email="owner@example.com").make()
    contributor = Recipe(
        auth.User, username="contributor", email="contributor@example.com"
    ).make()
    project = Recipe(
        models.Project,
        email=owner.email,
        emails=[owner.email, contributor.email],
        status="READY",
    ).make()

    assert utils.can_administrate_project(project, owner)
    assert utils.can_administrate_project(project, contributor)


@pytest.mark.django_db
def test_switchtender_can_administrate_project(client):
    switchtender = Recipe(auth.User).make()
    group = auth.Group.objects.get(name="switchtender")
    switchtender.groups.add(group)
    project = Recipe(models.Project, status="READY").make()

    assert utils.can_administrate_project(project, switchtender)


@pytest.mark.django_db
def test_non_switchtender_cannot_administrate_project(client):
    someone = Recipe(auth.User).make()
    project = Recipe(models.Project, status="READY").make()

    assert not utils.can_administrate_project(project, someone)


@pytest.mark.django_db
def test_non_staff_cannot_add_email_to_project(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-access-update", args=[project.id])

    with login(client, is_staff=False):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_add_email_to_project(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "test@example.com"}

    with login(client, groups=["switchtender"]):
        client.post(url, data=data)

    project = models.Project.objects.get(id=project.id)
    assert data["email"] in project.emails

    # detail_url = reverse("projects-project-detail", args=[project.id])
    # assertRedirects(response, detail_url)


@pytest.mark.django_db
def test_owner_can_add_email_to_project_if_not_draft(client):
    email = "owner@example.com"
    project = Recipe(models.Project, email=email, status="READY").make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, email=email, is_staff=False):
        client.post(url, data=data)

    project = models.Project.objects.get(id=project.id)
    assert data["email"] in project.emails


@pytest.mark.django_db
def test_owner_cannot_add_email_to_project_if_draft(client):
    email = "owner@example.com"
    project = Recipe(models.Project, email=email, status="DRAFT").make()
    url = reverse("projects-access-update", args=[project.id])
    data = {"email": "collaborator@example.com"}

    with login(client, email=email, is_staff=False):
        response = client.post(url, data=data)

    assert response.status_code == 403


@pytest.mark.django_db
def test_non_staff_cannot_delete_email_from_project(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-access-delete", args=[project.id, "test@example.com"])

    with login(client, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_owner_can_remove_email_from_project_if_not_draft(client):
    email = "owner@example.com"
    colab_email = "collaborator@example.com"
    project = Recipe(
        models.Project, email=email, emails=[email, colab_email], status="READY"
    ).make()
    url = reverse(
        "projects-access-delete",
        args=[project.id, colab_email],
    )

    with login(client, email=email, is_staff=False):
        client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert colab_email not in project.emails


@pytest.mark.django_db
def test_owner_cannot_remove_email_from_project_if_draft(client):
    email = "owner@example.com"
    colab_email = "collaborator@example.com"
    project = Recipe(
        models.Project, email=email, emails=[email, colab_email], status="DRAFT"
    ).make()
    url = reverse("projects-access-delete", args=[project.id, colab_email])

    with login(client, email=email, is_staff=False):
        response = client.post(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_switchtender_can_delete_email_from_project(client):
    email = "test@example.com"
    project = Recipe(models.Project, emails=[email]).make()
    url = reverse("projects-access-delete", args=[project.id, email])

    with login(client, groups=["switchtender"]):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert email not in project.emails

    update_url = reverse("projects-access-update", args=[project.id])
    assertRedirects(response, update_url)


@pytest.mark.django_db
def test_owner_cannot_be_removed_from_project_acl(client):
    email = "test@example.com"
    project = Recipe(models.Project, email=email, emails=[email]).make()
    url = reverse("projects-access-delete", args=[project.id, email])

    with login(client, groups=["switchtender"]):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert email in project.emails

    update_url = reverse("projects-access-update", args=[project.id])
    assertRedirects(response, update_url)


########################################################################
# Project syndication feed
########################################################################


@pytest.mark.django_db
def test_projects_feed_available_for_all_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-feed")
    response = client.get(url)
    detail_url = reverse("projects-project-detail", args=[project.id])
    assertContains(response, detail_url)


########################################################################
# tasks
########################################################################


#
# create


@pytest.mark.django_db
def test_create_task_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-task", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-task", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)

    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-task"')


@pytest.mark.django_db
def test_create_task_assigns_new_switchtender(client):
    project = Recipe(models.Project, switchtender=None).make()
    url = reverse("projects-create-task", args=[project.id])
    with login(client, groups=["switchtender"]):
        client.post(
            url,
            data={"content": "this is some content", "notify_email": False},
        )

    project = models.Project.objects.all()[0]
    assert project.switchtender is not None


@pytest.mark.django_db
def test_create_new_task_for_project_notify_user(mocker, client):
    project = Recipe(models.Project).make()
    mocker.patch("urbanvitaliz.apps.projects.views.tasks.notify_email_action_created")
    with login(client, groups=["switchtender"]):
        client.post(
            reverse("projects-create-task", args=[project.id]),
            data={"content": "this is some content", "notify_email": True},
        )

    views.tasks.notify_email_action_created.assert_called_once()


@pytest.mark.django_db
def test_create_new_task_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    username = "bob"
    with login(client, username=username, groups=["switchtender"]):
        response = client.post(
            reverse("projects-create-task", args=[project.id]),
            data={"content": "this is some content"},
        )
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.created_by.username == username
    assert response.status_code == 302


#
# Visit


@pytest.mark.django_db
def test_visit_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, resource=None).make()
    with login(client, email=owner_email):
        response = client.get(
            reverse("projects-visit-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.visited is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_visit_task_for_project_and_redirect_to_resource_for_project_owner(client):
    owner_email = "owner@univer.se"
    resource = resources.Resource()
    resource.save()

    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, resource=resource).make()
    with login(client, email=owner_email):
        response = client.get(
            reverse("projects-visit-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.visited is True
    assert response.status_code == 302


#
# mark as done
@pytest.mark.django_db
def test_new_task_toggle_done_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=True, done=False).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-toggle-done-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.done is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_done_task_toggle_done_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=True, done=True).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-toggle-done-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.done is False
    assert response.status_code == 302


@pytest.mark.django_db
def test_refuse_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, done=False).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-refuse-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.refused is True
    assert task.done is False
    assert response.status_code == 302


@pytest.mark.django_db
def test_already_done_task_for_project_and_redirect_for_project_owner(client):
    owner_email = "owner@univer.se"
    project = Recipe(
        models.Project, status="READY", email=owner_email, emails=[owner_email]
    ).make()
    task = Recipe(models.Task, project=project, visited=False, done=False).make()
    with login(client, email=owner_email):
        response = client.post(
            reverse("projects-already-done-task", args=[task.id]),
        )
    task = models.Task.objects.all()[0]
    assert task.refused is True
    assert task.done is True
    assert response.status_code == 302


#
# update


@pytest.mark.django_db
def test_update_task_not_available_for_non_staff_users(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-update-task", args=[task.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_task_available_for_switchtender(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-update-task", args=[task.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    # FIXME rename add-task to edit-task ?
    assertContains(response, 'form id="form-projects-add-task"')


@pytest.mark.django_db
def test_update_task_for_project_and_redirect(client):
    task = Recipe(models.Task).make()
    updated_on_before = task.updated_on
    url = reverse("projects-update-task", args=[task.id])
    data = {"content": "this is some content"}

    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    task = models.Task.objects.get(id=task.id)
    assert task.content == data["content"]
    assert task.updated_on > updated_on_before
    assert task.project.updated_on == task.updated_on

    assert response.status_code == 302


#
# delete


@pytest.mark.django_db
def test_delete_task_not_available_for_non_staff_users(client):
    task = Recipe(models.Task).make()
    url = reverse("projects-delete-task", args=[task.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_task_from_project_and_redirect(client):
    task = Recipe(models.Task).make()
    with login(client, groups=["switchtender"]):
        response = client.post(reverse("projects-delete-task", args=[task.id]))
    task = models.Task.deleted_objects.get(id=task.id)
    assert task.deleted
    assert response.status_code == 302


#
# reminder


@pytest.mark.django_db
def test_create_reminder_for_task(client):
    project = Recipe(models.Project, email="owner@example.com").make()
    task = Recipe(models.Task, project=project).make()
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
def test_create_reminder_without_delay_for_task(client):
    task = Recipe(models.Task, project__email="owner@example.com").make()
    url = reverse("projects-remind-task", args=[task.id])
    with login(client, email=task.project.email):
        response = client.post(url)
    assert response.status_code == 302
    assert reminders.Mail.to_send.count() == 1
    assert models.TaskFollowupRsvp.objects.count() == 1


@pytest.mark.django_db
def test_recreate_reminder_after_for_same_task(client):
    task = Recipe(models.Task, project__email="owner@example.com").make()
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
def test_recreate_reminder_before_for_same_task(client):
    task = Recipe(models.Task, project__email="owner@example.com").make()
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
def test_user_cannot_followup_on_someone_else_task(client):
    task = baker.make(models.Task)
    with login(client):
        url = reverse("projects-followup-task", args=[task.id])
        response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_can_followup_on_personal_task(client):
    data = dict(comment="some comment")
    with login(client) as user:
        project = baker.make(models.Project, status="READY", email=user.email)
        task = baker.make(models.Task, project=project)
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)
    followup = models.TaskFollowup.objects.all()[0]
    assert followup.task == task
    assert followup.status == 0  # to be replaced by task status
    assert followup.comment == data["comment"]
    assert followup.who == user


@pytest.mark.django_db
def test_followup_triggers_notifications(client):
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
            email=user.email,
            emails=[user.email, collab.email],
        )
        task = baker.make(models.Task, project=project)
        url = reverse("projects-followup-task", args=[task.id])
        client.post(url, data=data)

    assert switchtender.notifications.unread().count() == 1
    assert collab.notifications.unread().count() == 1
    assert owner.notifications.unread().count() == 0


@pytest.mark.django_db
def test_user_is_redirected_after_followup_on_task(client):
    with login(client) as user:
        project = baker.make(models.Project, status="READY", email=user.email)
        task = baker.make(models.Task, project=project)
        url = reverse("projects-followup-task", args=[task.id])
        response = client.post(url)
    assert response.status_code == 302
    assert (
        response.url
        == reverse("projects-project-detail", args=[task.project.id]) + "#actions"
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
# notes
########################################################################

#
# create


@pytest.mark.django_db
def test_create_note_not_available_for_non_staff_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_note_available_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-create-note", args=[project.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_note_available_for_project_collaborators(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        url = reverse("projects-create-note", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_create_new_note_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    with login(client, groups=["switchtender"]):
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_public_note_for_project_collaborator_and_redirect(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert note.created_by is not None
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_private_note_not_available_for_project_collaborator(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": "this is some content", "public": False},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_private_note_hidden_from_project_members(client):
    user_email = "not@admin.here"
    project = Recipe(models.Project, status="READY", emails=[user_email]).make()

    note = Recipe(models.Note, content="short note", public=False).make()

    with login(client, username="project_owner", email=user_email, is_staff=False):
        response = client.get(project.get_absolute_url())

    assertNotContains(response, note.content)


@pytest.mark.django_db
def test_public_note_available_to_readers(client):
    user_email = "not@admin.here"
    note_content = "this is a public note"
    project = Recipe(models.Project, emails=[user_email], status="READY").make()
    with login(client, groups=["switchtender"]):
        response = client.post(
            reverse("projects-create-note", args=[project.id]),
            data={"content": note_content, "public": "True"},
        )

    with login(client, username="project_owner", email=user_email, is_staff=False):
        response = client.get(project.get_absolute_url())

    assertContains(response, note_content)


#
# update


@pytest.mark.django_db
def test_update_note_not_available_for_non_staff_users(client):
    note = Recipe(models.Note).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_update_note_available_for_switchtender(client):
    note = Recipe(models.Note).make()
    url = reverse("projects-update-note", args=[note.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200
    # FIXME rename add-note to edit-note ?
    assertContains(response, 'form id="form-projects-add-note"')


@pytest.mark.django_db
def test_update_public_note_for_project_collaborator_and_redirect(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        note = Recipe(models.Note, project=project, public=True).make()
        response = client.post(
            reverse("projects-update-note", args=[note.id]),
            data={"content": "this is some content"},
        )
    note = models.Note.fetch()[0]
    assert note.project == project
    assert note.public is True
    assert response.status_code == 302


@pytest.mark.django_db
def test_update_private_note_for_project_collaborator(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email).make()
        note = Recipe(models.Note, project=project, public=False).make()
        url = reverse("projects-update-note", args=[note.id])
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_update_note_for_project_and_redirect(client):
    note = Recipe(models.Note).make()
    updated_on_before = note.updated_on
    url = reverse("projects-update-note", args=[note.id])
    data = {"content": "this is some content"}

    with login(client, groups=["switchtender"]):
        response = client.post(url, data=data)

    note = models.Note.objects.get(id=note.id)
    assert note.content == data["content"]
    assert note.updated_on > updated_on_before
    assert note.project.updated_on == note.updated_on

    assert response.status_code == 302


@pytest.mark.django_db
def test_delete_note_for_project_and_redirect(client):
    project = Recipe(models.Project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-delete-note", args=[note.id])

    with login(client, groups=["switchtender"]):
        response = client.post(url)

    assert models.Note.objects.count() == 0

    assert response.status_code == 302


########################################################################
# pushing a resource to a project's owner
########################################################################


@pytest.mark.django_db
def test_switchtender_push_resource_to_project_needs_project_id(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        session = client.session
        session["active_project"] = project.id
        session.save()
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_switchtender_push_resource_to_project_fails_if_no_project_in_session(client):
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_switchtender_push_resource_assigns_switchtender_to_project(client):
    project = Recipe(models.Project, switchtender=None).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        session = client.session
        session["active_project"] = project.id
        session.save()
        data = {"intent": "read this", "content": "some nice content"}
        client.post(url, data=data)

    project = models.Project.objects.get(pk=project.id)
    assert project.switchtender is not None


@pytest.mark.django_db
def test_switchtender_create_action_for_resource_push(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        session = client.session
        session["active_project"] = project.id
        session.save()

        data = {"intent": "read this", "content": "some nice content"}
        response = client.post(url, data=data)

    # a new Task is created
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.resource == resource
    assert task.content == data["content"]
    assert task.intent == data["intent"]
    # user is redirected to poject
    newurl = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, newurl)
    # sessions is cleaned up
    assert "project_id" not in client.session


@pytest.mark.django_db
def test_switchtender_create_action_for_resource_push_with_notification(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, public=True).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        # project_id should be in session
        session = client.session
        session["active_project"] = project.id
        session.save()

        data = {
            "intent": "read this",
            "content": "some nice content",
            "notify_email": True,
        }
        response = client.post(url, data=data)

    # a new Recommmendation is created
    task = models.Task.objects.all()[0]
    assert task.project == project
    assert task.resource == resource
    assert task.content == data["content"]
    assert task.intent == data["intent"]

    # notification is found
    assert len(get_messages(response.wsgi_request)) > 0

    # user is redirected to project
    newurl = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, newurl)
    # sessions is cleaned up
    assert "project_id" not in client.session


########################################################################
# Task Recommendation
########################################################################


@pytest.mark.django_db
def test_task_recommendation_list_not_available_for_non_staff(client):
    url = reverse("projects-task-recommendation-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_recommendation_list_available_for_staff(client):
    url = reverse("projects-task-recommendation-list")
    with login(client, is_staff=True):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_create_not_available_for_non_staff(client):
    url = reverse("projects-task-recommendation-create")
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_task_recommendation_available_for_staff(client):
    url = reverse("projects-task-recommendation-create")
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_is_created(client):
    url = reverse("projects-task-recommendation-create")
    resource = Recipe(resources.Resource).make()

    data = {"text": "mew", "resource": resource.pk}
    with login(client, is_staff=True):
        response = client.post(url, data=data)

    assert models.TaskRecommendation.objects.count() == 1

    assert response.status_code == 302
    newurl = reverse("projects-task-recommendation-list")
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_task_recommendation_update_not_available_for_non_staff(client):
    recommendation = Recipe(models.TaskRecommendation).make()
    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_recommendation_update_available_for_staff(client):
    recommendation = Recipe(models.TaskRecommendation).make()
    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))
    with login(client, is_staff=True):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_recommendation_is_updated(client):
    recommendation = Recipe(models.TaskRecommendation).make()

    url = reverse("projects-task-recommendation-update", args=(recommendation.pk,))

    data = {"text": "new-text", "resource": recommendation.resource.pk}
    with login(client, is_staff=True):
        response = client.post(url, data=data)

    assert response.status_code == 302
    newurl = reverse("projects-task-recommendation-list")
    assertRedirects(response, newurl)

    assert models.TaskRecommendation.objects.count() == 1
    updated_recommendation = models.TaskRecommendation.objects.all()[0]
    assert updated_recommendation.text == data["text"]


@pytest.mark.django_db
def test_task_suggestion_not_available_for_non_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_task_suggestion_when_no_survey(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_bare_project(client):
    Recipe(survey_models.Survey, pk=1).make()
    Recipe(models.TaskRecommendation, condition="").make()
    project = Recipe(models.Project).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_filled_project(client):
    Recipe(survey_models.Survey, pk=1).make()
    commune = Recipe(geomatics.Commune).make()
    Recipe(models.TaskRecommendation, condition="").make()
    project = Recipe(models.Project, commune=commune).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_task_suggestion_available_with_localized_reco(client):
    Recipe(survey_models.Survey, pk=1).make()
    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()
    Recipe(
        models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(models.Project, commune=commune).make()
    url = reverse("projects-project-tasks-suggest", args=(project.pk,))
    with login(client, groups=["switchtender"]):
        response = client.get(url)
    assert response.status_code == 200


########################################################################
# template tags and filters
########################################################################


@pytest.mark.django_db
def test_current_project_tag():
    project = Recipe(models.Project).make()
    session = {"project_id": project.id}
    assert projects_extra.current_project(session) == project


########################################################################
# REST API
########################################################################
@pytest.mark.django_db
def test_anonymous_cannot_use_project_api(client):
    url = reverse("projects-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_can_use_project_api(client):
    url = reverse("projects-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 200


########################################################################
# Utils
########################################################################
@pytest.mark.django_db
def test_get_switchtender_for_project(client):
    group = auth.Group.objects.get(name="switchtender")

    dept62 = baker.make(geomatics.Department, code="62")
    dept80 = baker.make(geomatics.Department, code="80")
    dept59 = baker.make(geomatics.Department, code="59")

    switchtenderA = baker.make(auth.User, groups=[group])
    switchtenderA.profile.departments.set([dept62, dept80])

    switchtenderB = baker.make(auth.User, groups=[group])
    switchtenderB.profile.departments.set([dept59, dept80])

    switchtenderC = baker.make(auth.User, groups=[group])
    switchtenderC.profile.departments.set([])

    project = baker.make(models.Project, status="READY", commune__department=dept62)

    selected_switchtenders = utils.get_switchtenders_for_project(project)

    assert len(selected_switchtenders) == 2
    assert switchtenderA in selected_switchtenders
    assert switchtenderB not in selected_switchtenders
    assert switchtenderC in selected_switchtenders


# eof
