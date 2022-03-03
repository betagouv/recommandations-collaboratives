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
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import notify
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertRedirects)
from urbanvitaliz.apps.communication import models as communication
from urbanvitaliz.apps.geomatics import models as geomatics
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
    project = models.Project.objects.all()[0]
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
    project = models.Project.objects.all()[0]
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
    project = models.Project.fetch()[0]
    assert response.status_code == 302
    url = reverse("projects-onboarding-select-commune", args=[project.id])
    assert response.url == (url)


@pytest.mark.django_db
def test_selecting_proper_commune_completes_project_creation(client):
    commune = Recipe(geomatics.Commune, postal="12345").make()
    selected = Recipe(geomatics.Commune, postal="12345").make()
    with login(client) as user:
        project = Recipe(models.Project, email=user.email, commune=commune).make()
        response = client.post(
            reverse("projects-onboarding-select-commune", args=[project.id]),
            data={"commune": selected.id},
        )
    project = models.Project.objects.get(id=project.id)
    assert project.commune == selected
    assert response.status_code == 302
    expected = reverse("survey-project-session", args=[project.id]) + "?first_time=1"
    assert response.url == expected


@pytest.mark.django_db
def test_proper_commune_selection_contains_all_possible_commmunes(client):
    expected = [
        Recipe(geomatics.Commune, postal="12345").make(),
        Recipe(geomatics.Commune, postal="12345").make(),
    ]
    unexpected = Recipe(geomatics.Commune, postal="67890").make()

    with login(client) as user:
        project = Recipe(models.Project, email=user.email, commune=expected[1]).make()
        response = client.get(
            reverse("projects-onboarding-select-commune", args=[project.id]),
        )
    page = str(response.content)
    for commune in expected:
        assert commune.name in page
    assert unexpected.name not in page


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
def test_project_detail_available_for_restricted_switchtender(client):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(models.Project, commune__departments__code="01").make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 200


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
def test_project_detail_contains_actions_for_switchtender(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-project-detail", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
        response = client.get(url)
    add_task_url = reverse("projects-project-create-action", args=[project.id])
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
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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
    Recipe(auth.Group, name="project_moderator").make()
    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, groups=["project_moderator", "switchtender"]):
        response = client.post(url)

    project = models.Project.objects.get(id=project.id)
    assert project.status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertRedirects(response, detail_url)


@pytest.mark.django_db
def test_accept_project_notifies_regional_actors(client):
    st_group, created = auth.Group.objects.get_or_create(name="switchtender")
    auth.Group.objects.get_or_create(name="project_moderator")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()
    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)

    project = Recipe(models.Project, commune=commune, email=regional_actor.email).make()

    with login(client, groups=["switchtender", "project_moderator"]):
        client.post(reverse("projects-project-accept", args=[project.id]))

    assert regional_actor.notifications.count() == 1


@pytest.mark.django_db
def test_accept_project_does_not_notify_non_regional_actors(client):
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
    project = Recipe(models.Project, commune=commune, email=owner.email).make()

    with login(client, groups=["switchtender"]):
        client.post(reverse("projects-project-accept", args=[project.id]))

    assert non_regional_actor.notifications.count() == 0


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


@pytest.mark.django_db
def test_notifications_are_deleted_on_project_delete():
    user = Recipe(auth.User, username="Bob", first_name="Bobi", last_name="Joe").make()
    recipient = Recipe(auth.User).make()

    project = Recipe(models.Project).make()

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


@pytest.mark.django_db
def test_notifications_are_deleted_on_task_delete():
    user = Recipe(auth.User).make()
    recipient = Recipe(auth.User).make()

    task = Recipe(models.Task).make()

    notify.send(
        sender=user,
        recipient=recipient,
        verb="a reçu une notif",
        action_object=task,
        target=task.project,
    )

    assert recipient.notifications.count() == 1
    task.delete()
    assert recipient.notifications.count() == 0


########################################################################
# modify who can access the project
########################################################################


def test_notification_not_sent_when_project_is_draft():
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(models.Project, status="DRAFT", emails=[user.email])

    # Generate a notification
    signals.action_created.send(
        sender=test_notification_not_sent_when_project_is_draft,
        task=models.Task.objects.create(project=project, created_by=switchtender),
        project=project,
        user=switchtender,
    )

    assert user.notifications.unsent().count() == 0


def test_notification_not_sent_when_project_is_muted():
    user = Recipe(auth.User, username="auser", email="user@example.com").make()
    switchtender = Recipe(
        auth.User, username="switchtender", email="switchtender@example.com"
    ).make()
    project = baker.make(
        models.Project, status="READY", muted=True, emails=[user.email]
    )

    # Generate a notification
    signals.action_created.send(
        sender=test_notification_not_sent_when_project_is_draft,
        task=models.Task.objects.create(project=project, created_by=switchtender),
        project=project,
        user=switchtender,
    )

    assert user.notifications.unsent().count() == 0


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

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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


#
# reminder


@pytest.mark.django_db
def test_create_reminder_for_task(client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
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
    baker.make(communication.EmailTemplate, name="rsvp_reco")
    task = Recipe(models.Task, project__email="owner@example.com").make()
    url = reverse("projects-remind-task", args=[task.id])
    with login(client, email=task.project.email):
        response = client.post(url)
    assert response.status_code == 302
    assert reminders.Mail.to_send.count() == 1
    assert models.TaskFollowupRsvp.objects.count() == 1


@pytest.mark.django_db
def test_recreate_reminder_after_for_same_task(client):
    baker.make(communication.EmailTemplate, name="rsvp_reco")
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
    baker.make(communication.EmailTemplate, name="rsvp_reco")
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
            switchtenders=[switchtender],
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

# Public conversation
@pytest.mark.django_db
def test_create_conversation_message_not_available_for_non_logged_users(client):
    project = Recipe(models.Project).make()
    url = reverse("projects-conversation-create-message", args=[project.id])
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_create_conversation_message_not_available_for_outsiders(client):
    with login(client):
        project = Recipe(models.Project).make()
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    assert response.status_code == 403


@pytest.mark.django_db
def test_create_conversation_message_available_for_project_collaborators(client):
    with login(client) as user:
        project = Recipe(models.Project, email=user.email, status="READY").make()
        url = reverse("projects-conversation-create-message", args=[project.id])
        response = client.post(
            url,
            data={"content": "this is some content"},
        )
    note = models.Note.objects.all()[0]
    assert note.project == project
    assert response.status_code == 302


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
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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
    with login(client, groups=["switchtender"]) as user:
        project.switchtenders.add(user)
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
    with login(client, groups=["switchtender"]) as user:
        note.project.switchtenders.add(user)
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

    with login(client, groups=["switchtender"]) as user:
        note.project.switchtenders.add(user)
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
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        session = client.session
        session["active_project"] = project.id
        session.save()
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_switchtender_push_resource_to_project_fails_if_no_project_in_session(client):
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_switchtender_push_resource_assigns_switchtender_to_project(client):
    project = Recipe(models.Project, switchtenders=[]).make()
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["switchtender"]):
        session = client.session
        session["active_project"] = project.id
        session.save()
        data = {"intent": "read this", "content": "some nice content"}
        client.post(url, data=data)

    project = models.Project.objects.get(pk=project.id)
    assert project.switchtenders.count() == 1


@pytest.mark.django_db
def test_switchtender_create_action_for_resource_push(client):
    project = Recipe(models.Project).make()
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

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
def test_switchtender_joins_project(client):
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

    url = reverse("projects-project-switchtender-join", args=[project.id])
    with login(client, groups=["switchtender"]) as user:
        # Test GET
        response = client.get(url)
        assert response.status_code == 200

        # Then POST to join projet
        response = client.post(url)

    project = models.Project.objects.get(pk=project.pk)

    assert response.status_code == 302
    assert project.switchtenders.count() == 1
    assert project.switchtenders.first() == user


# eof
