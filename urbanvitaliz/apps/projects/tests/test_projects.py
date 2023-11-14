# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

import csv
import io

import pytest
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import get_user_perms
from model_bakery import baker
from model_bakery.recipe import Recipe
from notifications import notify
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects
from urbanvitaliz import verbs
from urbanvitaliz.apps.geomatics import models as geomatics
from urbanvitaliz.apps.home import models as home_models
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.apps.resources import models as resources
from urbanvitaliz.apps.tasks import models as task_models
from urbanvitaliz.apps.tasks import signals
from urbanvitaliz.utils import get_group_for_site, login

from .. import models, utils

# TODO when local authority can see & update her project
# TODO check that project, note, and task belong to her


########################################################################
# Landing page
########################################################################


@pytest.mark.django_db
def test_home_page_is_reachable_without_login(client):
    url = reverse("home")
    response = client.get(url)
    assert response.status_code == 200
    assertContains(response, "UrbanVitaliz")


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
@override_settings(DEBUG=True)
def test_existing_user_receives_email_on_login(client, settings, mailoutbox):  # noqa
    user = Recipe(auth.User, email="jdoe@example.com").make()
    url = reverse("magicauth-login")

    response = client.post(url, data={"email": user.email})

    assert response.status_code == 302
    assert len(mailoutbox) == 1
    assert user.email in mailoutbox[0].to


@pytest.mark.django_db
def test_unknown_user_is_created_and_receives_email_on_login(client, mailoutbox):
    email = "jdoe@example.com"
    url = reverse("magicauth-login")
    response = client.post(url, data={"email": email})
    assert response.status_code == 302
    assert auth.User.objects.get(email=email)
    assert len(mailoutbox) == 1
    assert email in mailoutbox[0].to


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
def test_project_list_available_for_switchtender_user(request, client):
    get_current_site(request)
    url = reverse("projects-project-list")
    with login(client, groups=["example_com_advisor"]):
        response = client.get(url, follow=True)

    advisor_url = reverse("projects-project-list-advisor")
    url, code = response.redirect_chain[-1]
    assert code == 302
    assert url == advisor_url


@pytest.mark.django_db
def test_project_list_available_for_staff(request, client):
    get_current_site(request)
    url = reverse("projects-project-list")
    with login(client, groups=["example_com_staff", "example_com_advisor"]):
        response = client.get(url, follow=True)

    staff_url = reverse("projects-project-list-staff")
    url, code = response.redirect_chain[-1]
    assert code == 302
    assert url == staff_url


@pytest.mark.django_db
def test_project_list_excludes_project_not_in_switchtender_departments(request, client):
    department = Recipe(geomatics.Department, code="00").make()
    site = get_current_site(request)
    project = Recipe(
        models.Project,
        sites=[site],
        commune__department__code="01",
    ).make()
    url = reverse("projects-project-list")
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)
        user.profile.departments.add(department)
        response = client.get(url, follow=True)

    detail_url = reverse("projects-project-detail", args=[project.id])
    assertNotContains(response, detail_url)


@pytest.mark.django_db
def test_draft_project_list_available_for_staff(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site], status="DRAFT")

    url = reverse("projects-project-list-staff")
    with login(client, groups=["example_com_staff"]):
        response = client.get(url, follow=True)

    assert response.status_code == 200
    assertContains(response, reverse("projects-project-detail", args=[project.id]))


########################################################################
# Project details
########################################################################


# Overview
@pytest.mark.django_db
def test_project_overview_not_available_for_unprivileged_user(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-overview", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_overview_available_for_owner(request, client):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    # project email is same as test user to be logged in
    project = Recipe(models.Project, sites=[current_site]).make()

    with login(client) as user:
        utils.assign_collaborator(user, project, is_owner=True)
        url = reverse("projects-project-detail-overview", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_overview_available_for_switchtender(request, client):
    site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=site,
        onboarding=onboarding,
    )

    project = Recipe(models.Project, sites=[site]).make()
    url = reverse("projects-project-detail-overview", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)
        response = client.get(url)
    assert response.status_code == 200


# Knowledge
@pytest.mark.django_db
def test_project_knowledge_not_available_for_unprivileged_user(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_knowledge_available_for_owner(request, client):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    # project email is same as test user to be logged in
    owner = baker.make(auth.User, is_staff=False)

    project = Recipe(models.Project, sites=[current_site]).make()

    utils.assign_collaborator(owner, project, is_owner=True)

    with login(client, user=owner, is_staff=False):
        url = reverse("projects-project-detail-knowledge", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_switchtender(request, client):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, current_site)
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_knowledge_available_for_restricted_switchtender(request, client):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        sites=[current_site],
        commune__departments__code="01",
    ).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, current_site)
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
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
    ).make()

    with login(client) as user:
        utils.assign_collaborator(user, project)
        url = reverse("projects-project-detail-actions", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_actions_available_for_switchtender(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_actions_available_for_restricted_switchtender(request, client):
    other = Recipe(geomatics.Department, code="02").make()
    site = get_current_site(request)
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[site],
    ).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 200


# conversations
@pytest.mark.django_db
def test_project_conversations_not_available_for_unprivileged_user(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_conversations_available_for_owner(request, client):
    project = Recipe(
        models.Project,
        sites=[get_current_site(request)],
    ).make()

    with login(client) as user:
        utils.assign_collaborator(user, project, is_owner=True)
        url = reverse("projects-project-detail-conversations", args=[project.id])
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_conversations_available_for_regional_advisor(request, client):
    dpt = Recipe(geomatics.Department, code="01").make()
    site = get_current_site(request)
    project = Recipe(models.Project, commune__department=dpt, sites=[site]).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)
        user.profile.departments.add(dpt)
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_conversations_available_for_assigned_advisor(request, client):
    site = get_current_site(request)

    project = Recipe(models.Project, sites=[site]).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])

    with login(client) as user:
        utils.assign_advisor(user, project, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_project_conversations_not_available_for_nonregional_advisor(request, client):
    other = Recipe(geomatics.Department, code="02").make()
    site = get_current_site(request)
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[site],
    ).make()
    url = reverse("projects-project-detail-conversations", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 403


#
# internal
@pytest.mark.django_db
def test_project_internal_followup_not_available_for_common_user(request, client):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse("projects-project-detail-internal-followup", args=[project.id])
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_not_available_for_owner(request, client):
    # project email is same as test user to be logged in
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

    with login(client) as user:
        utils.assign_collaborator(user, project, is_owner=True)
        url = reverse("projects-project-detail-internal-followup", args=[project.id])
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_available_for_assigned_advisor(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse("projects-project-detail-internal-followup", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, current_site)
        response = client.get(url)
    assert response.status_code == 200


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
    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 403


#
# internal tracking
@pytest.mark.django_db
def test_project_internal_followup_tracking_not_available_for_common_user(
    request, client
):
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()
    url = reverse(
        "projects-project-detail-internal-followup-tracking", args=[project.id]
    )
    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_tracking_not_available_for_owner(request, client):
    # project email is same as test user to be logged in
    project = Recipe(models.Project, sites=[get_current_site(request)]).make()

    with login(client) as user:
        utils.assign_collaborator(user, project, is_owner=True)
        url = reverse(
            "projects-project-detail-internal-followup-tracking", args=[project.id]
        )
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_internal_followup_tracking_available_for_assigned_advisor(
    request, client
):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    url = reverse(
        "projects-project-detail-internal-followup-tracking", args=[project.id]
    )
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, current_site)
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_internal_followup_tracking_not_available_for_restricted_switchtender(
    request, client
):
    other = Recipe(geomatics.Department, code="02").make()
    project = Recipe(
        models.Project,
        commune__departments__code="01",
        sites=[get_current_site(request)],
    ).make()
    url = reverse(
        "projects-project-detail-internal-followup-tracking", args=[project.id]
    )
    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.departments.add(other)
        response = client.get(url)
    assert response.status_code == 403


#
# project details overview


@pytest.mark.django_db
def test_project_detail_contains_informations(request, client):
    current_site = get_current_site(request)
    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=current_site,
        onboarding=onboarding,
    )

    project = Recipe(models.Project, sites=[current_site]).make()
    task = Recipe(task_models.Task, project=project).make()
    note = Recipe(models.Note, project=project).make()
    url = reverse("projects-project-detail-knowledge", args=[project.id])
    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)
    assertContains(response, project.description)
    assertContains(response, task.content)
    assertContains(response, note.content)


@pytest.mark.skip(reason="waiting for UI fix")
@pytest.mark.django_db
def test_project_detail_contains_actions_for_assigned_advisor(request, client):
    site = get_current_site(request)

    project = Recipe(models.Project, sites=[site]).make()
    url = reverse("projects-project-detail-actions", args=[project.id])
    with login(client) as user:
        utils.assign_advisor(user, project, site)

        response = client.get(url)
    assert response.status_code == 200

    add_task_url = reverse("projects-project-create-task", args=[project.id])
    assertContains(response, add_task_url)


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
    current_site = get_current_site(request)
    owner = Recipe(auth.User, username="owner@owner.co").make()
    project = Recipe(models.Project, sites=[current_site]).make()
    baker.make(models.ProjectMember, project=project, member=owner, is_owner=True)

    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert project.status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    # check updated permissions
    assert "invite_collaborators" in get_user_perms(owner, project)

    assert response.status_code == 302


@pytest.mark.django_db
def test_accept_project_without_owner_and_redirect(request, client):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()

    updated_on_before = project.updated_on
    url = reverse("projects-project-accept", args=[project.id])

    with login(client, groups=["example_com_staff"]) as moderator:
        moderator.profile.sites.add(current_site)
        response = client.post(url)

    project = models.Project.on_site.get(id=project.id)
    assert project.status == "TO_PROCESS"
    assert project.updated_on > updated_on_before

    assert response.status_code == 302


@pytest.mark.django_db
def test_accept_project_notifies_regional_actors(request, client):
    current_site = get_current_site(request)

    st_group = auth.Group.objects.get(name="example_com_advisor")

    dpt_nord = Recipe(geomatics.Department, code=59, name="Nord").make()
    commune = Recipe(
        geomatics.Commune, name="Lille", postal="59000", department=dpt_nord
    ).make()

    regional_actor = Recipe(auth.User).make()
    regional_actor.groups.add(st_group)
    regional_actor.profile.departments.add(dpt_nord)
    regional_actor.profile.sites.add(current_site)

    membership = baker.make(models.ProjectMember, member=regional_actor, is_owner=True)

    project = Recipe(
        models.Project,
        sites=[current_site],
        commune=commune,
        projectmember_set=[membership],
    ).make()

    with login(client, groups=["example_com_advisor", "example_com_staff"]) as user:
        user.profile.sites.add(current_site)
        client.post(reverse("projects-project-accept", args=[project.id]))

    assert regional_actor.notifications.count() == 1


@pytest.mark.django_db
def test_accept_project_does_not_notify_non_regional_actors(request, client):
    group = auth.Group.objects.get(name="example_com_advisor")

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

    with login(client, user=nr_membership.member, groups=["example_com_advisor"]):
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

    # delete needs staff, list projects needs advisor
    with login(client, groups=["example_com_staff"]):
        response = client.post(url)

    project = models.Project.deleted_on_site.get(id=project.id)
    assert project.deleted
    assert project.updated_on > updated_on_before

    list_url = reverse("projects-project-list")
    assert response.url == list_url


@pytest.mark.django_db
def test_general_notifications_are_consumed_on_project_overview(request, client):
    current_site = get_current_site(request)

    onboarding = onboarding_models.Onboarding.objects.first()

    baker.make(
        home_models.SiteConfiguration,
        site=get_current_site(request),
        onboarding=onboarding,
    )

    project = Recipe(
        models.Project,
        sites=[current_site],
        name="Proj1",
        location="Somewhere",
    ).make()

    with login(
        client, groups=["example_com_advisor"], is_staff=False, username="Bob"
    ) as user:
        notify.send(
            sender=user,
            recipient=user,
            verb=verbs.Project.BECAME_ADVISOR,
            target=project,
        )

        notify.send(  # should e a signal
            sender=project,
            recipient=user,
            verb=verbs.Project.VALIDATED,
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


@pytest.mark.django_db
def test_notification_not_sent_when_project_is_draft(request):
    switchtender = Recipe(
        auth.User, username="advisor", email="advisor@example.com"
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
        task=task_models.Task.objects.create(
            project=project,
            site=get_current_site(request),
            created_by=switchtender,
        ),
        project=project,
        user=switchtender,
    )

    assert membership.member.notifications.unsent().count() == 0


@pytest.mark.django_db
def test_notification_not_sent_when_project_is_muted(request):
    switchtender = Recipe(
        auth.User, username="advisor", email="advisor@example.com"
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
        task=task_models.Task.on_site.create(
            project=project, site=get_current_site(request), created_by=switchtender
        ),
        project=project,
        user=switchtender,
    )

    assert membership.member.notifications.unsent().count() == 0


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


########################################################################
# pushing a resource to a project's owner
########################################################################


@pytest.mark.django_db
def test_switchtender_push_resource_to_project_fails_if_no_project_in_session(client):
    resource = Recipe(resources.Resource, status=resources.Resource.PUBLISHED).make()

    url = reverse("projects-create-resource-action", args=[resource.id])
    with login(client, groups=["example_com_advisor"]):
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
    with login(client) as user:
        utils.assign_advisor(user, project, current_site)

        session = client.session
        session["active_project"] = project.id
        session.save()

        response = client.post(url)

    newurl = (
        reverse("projects-project-create-task", args=[project.id])
        + f"?resource={resource.id}"
    )
    assertRedirects(response, newurl)


@pytest.mark.django_db
def test_switchtender_joins_project(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()
    Recipe(
        task_models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    project = Recipe(models.Project, sites=[current_site], commune=commune).make()

    url = reverse("projects-project-switchtender-join", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

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
        task_models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site], commune=commune).make()

    url = reverse("projects-project-switchtender-leave", args=[project.id])
    with login(client) as user:
        utils.assign_advisor(user, project, site)

        assert project.switchtenders_on_site.count() == 1

        # Then POST to leave project
        response = client.post(url)

    project = models.Project.on_site.get(pk=project.pk)

    assert response.status_code == 302
    assert project.switchtenders.count() == 0


@pytest.mark.django_db
def test_advisor_joins_trigger_notification_to_all(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    collaborator = baker.make(auth.User)
    advisor = baker.make(auth.User)

    Recipe(
        task_models.TaskRecommendation,
        condition="",
        departments=[
            dept,
        ],
    ).make()

    project = Recipe(
        models.Project,
        status="READY",
        commune=commune,
        sites=[current_site],
    ).make()

    utils.assign_collaborator(collaborator, project, is_owner=True)
    utils.assign_advisor(advisor, project, current_site)

    url = reverse("projects-project-switchtender-join", args=[project.id])

    with login(client, groups=["example_com_advisor"]):
        client.post(url)

    assert collaborator.notifications.count() == 1
    assert advisor.notifications.count() == 1


@pytest.mark.django_db
def test_switchtender_joins_and_leaves_on_the_same_12h_should_not_notify(
    request, client
):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    dept = Recipe(geomatics.Department).make()

    membership = baker.make(models.ProjectMember, is_owner=True)

    Recipe(
        task_models.TaskRecommendation,
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
        sites=[current_site],
    ).make()

    join_url = reverse("projects-project-switchtender-join", args=[project.id])
    leave_url = reverse("projects-project-switchtender-leave", args=[project.id])
    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        client.post(join_url)
        assert membership.member.notifications.count() == 1

        client.post(leave_url)

        assert membership.member.notifications.count() == 0


#################################################################
# CSV
#################################################################


@pytest.mark.django_db
def test_switchtender_exports_csv(request, client):
    site = get_current_site(request)

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

    # Make a task
    Recipe(task_models.Task, public=True, project=p1).make()

    url = reverse("projects-project-list-export-csv")
    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, p1, site)

        response = client.get(url)

    assert response.status_code == 200

    content = response.content.decode("utf-8")
    cvs_reader = csv.reader(io.StringIO(content))
    body = list(cvs_reader)
    body.pop(0)

    assert len(body) == 1


#################################################################
# Tags
#################################################################
@pytest.mark.django_db
def test_advisor_cannot_updates_tags(request, client):
    current_site = get_current_site(request)

    project = Recipe(models.Project, sites=[current_site]).make()

    data = {"tags": "blah"}

    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, current_site)

        response = client.post(
            reverse("projects-project-tags", args=[project.id]), data=data
        )

    assert response.status_code == 403
    project = models.Project.objects.all()[0]
    assert list(project.tags.names()) == []


@pytest.mark.django_db
def test_staff_updates_tags(request, client):
    current_site = get_current_site(request)

    project = Recipe(models.Project, sites=[current_site]).make()

    data = {"tags": "blah"}

    with login(client, groups=["example_com_staff"]) as user:
        utils.assign_advisor(user, project, current_site)

        response = client.post(
            reverse("projects-project-tags", args=[project.id]), data=data
        )

    assert response.status_code == 302
    project = models.Project.objects.all()[0]
    assert list(project.tags.names()) == [data["tags"]]


#################################################################
# Topics
#################################################################


@pytest.mark.django_db
def test_switchtender_writes_advisors_note(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    with login(client) as user:
        utils.assign_advisor(user, project, site)

        response = client.post(
            reverse("projects-project-topics", args=[project.id]),
            data={
                "advisors_note": "this is some content",
                "form-TOTAL_FORMS": 1,
                "form-INITIAL_FORMS": 0,
            },
        )

    assert response.status_code == 302
    project = models.Project.objects.all()[0]
    assert project.advisors_note is not None
    assert project.advisors_note_on is not None
    assert project.advisors_note_by == user


@pytest.mark.django_db
def test_switchtender_view_project_topics(request, client):
    site = get_current_site(request)
    topic = Recipe(models.Topic, site=site, name="a nice topic").make()
    project = Recipe(models.Project, sites=[site], topics=[topic]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)

        response = client.get(
            reverse("projects-project-topics", args=[project.id]),
        )

    assert response.status_code == 200
    # TODO add this test when UI updated
    # assertContains(response, topic.name)


@pytest.mark.django_db
def test_switchtender_add_new_topic_to_project(request, client):
    site = get_current_site(request)
    project = Recipe(models.Project, sites=[site]).make()

    data = {
        "advisors_note": "",
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 0,
        "form-0-id": "",
        "form-0-name": "blah",
        "form-0-DELETE": False,
    }

    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)

        response = client.post(
            reverse("projects-project-topics", args=[project.id]),
            data=data,
        )

    assert response.status_code == 302

    assert models.Topic.objects.count() == 1
    topic = models.Topic.objects.first()
    assert topic.name == data["form-0-name"].capitalize()
    assert topic in project.topics.all()


@pytest.mark.django_db
def test_switchtender_add_existing_topic_to_project(request, client):
    site = get_current_site(request)

    topic = Recipe(models.Topic, site=site, name="blah").make()
    project = Recipe(models.Project, sites=[site]).make()

    data = {
        "advisors_note": "",
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 0,
        "form-0-id": "",
        "form-0-name": topic.name,
        "form-0-DELETE": False,
    }

    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)

        response = client.post(
            reverse("projects-project-topics", args=[project.id]),
            data=data,
        )

    assert response.status_code == 302

    assert models.Topic.objects.count() == 1
    assert topic in project.topics.all()


@pytest.mark.django_db
def test_switchtender_remove_topic_from_project(request, client):
    site = get_current_site(request)

    topic = Recipe(models.Topic, site=site, name="blah").make()
    project = Recipe(models.Project, sites=[site], topics=[topic]).make()

    data = {
        "advisors_note": "",
        "form-TOTAL_FORMS": 1,
        "form-INITIAL_FORMS": 0,
        "form-0-id": "",
        "form-0-name": topic.name,
        "form-0-DELETE": True,
    }

    with login(client, groups=["example_com_advisor"]) as user:
        utils.assign_advisor(user, project, site)

        response = client.post(
            reverse("projects-project-topics", args=[project.id]),
            data=data,
        )

    assert response.status_code == 302

    assert models.Topic.objects.count() == 1
    assert topic not in project.topics.all()


#################################################################
# User interest in project
#################################################################
@pytest.mark.django_db
def test_regional_switchtender_can_observe_project(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.departments.set([project.commune.department.pk])
        user.profile.sites.add(current_site)

        response = client.post(
            reverse("projects-project-observer-join", args=[project.id]),
        )

    assert response.status_code == 302
    project = models.Project.objects.all()[0]
    switchtending = models.ProjectSwitchtender.objects.get(
        project=project, switchtender=user
    )
    assert switchtending.is_observer is True


@pytest.mark.django_db
def test_non_regional_switchtender_can_observe_project(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        response = client.post(
            reverse("projects-project-observer-join", args=[project.id]),
        )

    assert response.status_code == 302


@pytest.mark.django_db
def test_switchtender_visits_project_without_interest(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        response = client.get(
            reverse("projects-project-detail-overview", args=[project.id]),
        )

    assert response.status_code == 200

    personal_status = models.UserProjectStatus.objects.get(project=project, user=user)

    assert personal_status.status == "TODO"


@pytest.mark.django_db
def test_switchtender_visits_new_project(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        Recipe(
            models.UserProjectStatus,
            site=current_site,
            project=project,
            user=user,
            status="NEW",
        ).make()

        response = client.get(
            reverse("projects-project-detail-overview", args=[project.id]),
        )

    assert response.status_code == 200

    personal_status = models.UserProjectStatus.objects.get(project=project, user=user)

    assert personal_status.status == "TODO"


@pytest.mark.django_db
def test_switchtender_observes_project_shows_interest(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        response = client.get(
            reverse("projects-project-detail-overview", args=[project.id]),
        )
        assert response.status_code == 200

        response = client.post(
            reverse("projects-project-observer-join", args=[project.id]),
        )
        assert response.status_code == 302

    personal_status = models.UserProjectStatus.objects.get(project=project, user=user)

    assert personal_status.status == "TODO"


@pytest.mark.django_db
def test_switchtender_advises_project_shows_interest(request, client):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        response = client.get(
            reverse("projects-project-detail-overview", args=[project.id]),
        )
        assert response.status_code == 200

        response = client.post(
            reverse("projects-project-switchtender-join", args=[project.id]),
        )
        assert response.status_code == 302

    personal_status = models.UserProjectStatus.objects.get(project=project, user=user)

    assert personal_status.status == "TODO"


@pytest.mark.django_db
def test_switchtender_stop_advising_or_observing_project_shows_no_interest(
    request, client
):
    current_site = get_current_site(request)

    commune = Recipe(geomatics.Commune).make()
    project = Recipe(models.Project, commune=commune, sites=[current_site]).make()

    with login(client, groups=["example_com_advisor"]) as user:
        user.profile.sites.add(current_site)

        response = client.get(
            reverse("projects-project-detail-overview", args=[project.id]),
        )
        assert response.status_code == 200

        response = client.post(
            reverse("projects-project-switchtender-join", args=[project.id]),
        )
        assert response.status_code == 302
        response = client.post(
            reverse("projects-project-switchtender-leave", args=[project.id]),
        )
        assert response.status_code == 302

    personal_status = models.UserProjectStatus.objects.get(project=project, user=user)

    assert personal_status.status == "NOT_INTERESTED"


########################################################################
# model level tests
########################################################################


@pytest.mark.django_db
def test_project_list_excludes_non_site_projects_for_user():
    current_site = sites.Site.objects.get_current()
    other_site = Recipe(sites.Site, domain="other.site").make()

    project = Recipe(
        models.Project, commune__name="one", status="READY", sites=[current_site]
    ).make()
    Recipe(
        models.Project, commune__name="dos", status="READY", sites=[other_site]
    ).make()
    Recipe(models.Project, commune__name="tres", status="READY", sites=[]).make()

    user = Recipe(auth.User).make()
    group = get_group_for_site("advisor", site=current_site)
    group.user_set.add(user)

    result = list(models.Project.on_site.for_user(user))

    assert result == [project]


#################################################################
# Activity flags
#################################################################
@pytest.mark.django_db
def test_last_members_activity_is_updated_by_public_comment_from_member(
    client, request
):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-conversation-create-message", kwargs={"project_id": project.pk}
    )

    before_update = timezone.now()

    with login(client) as owner:
        utils.assign_collaborator(owner, project, is_owner=True)
        response = client.post(url, data={"content": "this is some content"})

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.last_members_activity_at > before_update


@pytest.mark.django_db
def test_last_members_activity_not_updated_by_public_comment_from_advisor(
    client, request
):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-conversation-create-message", kwargs={"project_id": project.pk}
    )

    before_update = timezone.now()

    with login(client) as user:
        utils.assign_advisor(user, project)
        response = client.post(url, data={"content": "this is some content"})

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.last_members_activity_at < before_update


@pytest.mark.django_db
def test_last_members_activity_is_updated_by_document_upload_from_member(
    client, request
):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-documents-upload-document", kwargs={"project_id": project.pk}
    )

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")

    before_update = timezone.now()
    with login(client) as owner:
        utils.assign_collaborator(owner, project, is_owner=True)
        response = client.post(
            url, data={"description": "this is some content", "the_file": png}
        )

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.last_members_activity_at > before_update


@pytest.mark.django_db
def test_last_members_activity_not_updated_by_document_upload_from_advisor(
    client, request
):
    site = get_current_site(request)

    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
    )

    url = reverse(
        "projects-documents-upload-document", kwargs={"project_id": project.pk}
    )

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")

    before_update = timezone.now()

    with login(client) as user:
        utils.assign_advisor(user, project)
        response = client.post(
            url, data={"description": "this is some content", "the_file": png}
        )

    assert response.status_code == 302

    project.refresh_from_db()

    assert project.last_members_activity_at < before_update


# eof
