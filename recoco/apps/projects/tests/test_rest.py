# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from actstream.models import user_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from notifications.signals import notify
from pytest_django.asserts import assertContains
from rest_framework.test import APIClient

from recoco import verbs
from recoco.apps.tasks import models as tasks_models
from recoco.utils import login

from .. import models, utils

########################################################################
# list of projects
########################################################################

# FIXME pourquoi est ce que ces tests n'utilisent pas le APIClient ?


@pytest.mark.django_db
def test_anonymous_cannot_use_project_list_api(client):
    url = reverse("projects-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_in_user_can_use_project_api(client):
    url = reverse("projects-list")
    with login(client):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_includes_project_for_advisor(request, client):
    current_site = get_current_site(request)
    project = baker.make(
        models.Project, commune__name="Lille", sites=[current_site], status="READY"
    )
    url = reverse("projects-list")

    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_project_for_staff(request, client):
    current_site = get_current_site(request)
    project = baker.make(models.Project, sites=[current_site], status="READY")
    url = reverse("projects-list")

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_only_projects_in_switchtender_departments(
    request, client
):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__name="Ma Comune",
        commune__department__code="01",
        commune__department__name="Mon Departement",
        name="Mon project",
    )

    # a public note with notification
    pub_note = baker.make(models.Note, public=True, project=project)
    verb = verbs.Conversation.PUBLIC_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=project)
    verb = verbs.Conversation.PRIVATE_MESSAGE
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    baker.make(  # unwanted project
        models.Project,
        sites=[site],
        status="READY",
        commune__department__code="02",
    )

    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("projects-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    data = response.data["results"][0]

    # project fields: not ideal
    expected = [
        "commune",
        "created_on",
        "id",
        "inactive_since",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "status",
        "switchtenders",
        "updated_on",
    ]
    assert set(data.keys()) == set(expected)

    assert data["name"] == project.name
    assert data["is_switchtender"] is True
    assert data["is_observer"] is False
    assert data["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
        "project_id": str(project.id),
    }


########################################################################
# get project details
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_project_detail_api(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("projects-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_simple_user_cannot_use_project_detail_api(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = create_project_with_notifications(site, user)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("projects-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_contains_project_info(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = create_project_with_notifications(site, user)

    utils.assign_advisor(user, project, site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("projects-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 200

    data = response.data
    check_project_content(project, data)


def create_project_with_notifications(site, user):
    """Create a new project with user as advisor and notifications

    To keep in sync with check_project_content
    """
    # my project and details
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__name="Ma Comune",
        commune__department__code="01",
        commune__department__name="Mon Departement",
        name="Mon project",
    )

    # a public note with notification
    pub_note = baker.make(models.Note, public=True, project=project)
    verb = verbs.Conversation.PUBLIC_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=project)
    verb = verbs.Conversation.PRIVATE_MESSAGE
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    return project


def check_project_content(project, data):
    """Check project content provided as json

    To keep in sync with create_project_with_notifications
    """
    # project fields: not ideal
    expected = [
        "commune",
        "created_on",
        "id",
        "inactive_since",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "status",
        "switchtenders",
        "updated_on",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
    ]
    assert set(data.keys()) == set(expected)

    assert data["name"] == project.name
    assert data["is_switchtender"] is True
    assert data["is_observer"] is False
    assert data["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
    }


########################################################################
# patch project details
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_project_patch_api(request, client):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site], status="DRAFT")

    client = APIClient()

    url = reverse("projects-detail", args=[project.id])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_project_is_reported_by_project_patch_api(client):
    user = baker.make(auth_models.User, email="me@example.com")

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("projects-detail", args=[0])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 404


# XXX Following test returns a 200 and no error on failed processing
# @pytest.mark.django_db
# def test_bad_processing_is_reported_by_project_patch_api(request, client):
#     site = get_current_site(request)
#     user = baker.make(auth_models.User, email="me@example.com")
#     project = baker.make(models.Project, sites=[site], status="DRAFT")
#
#     client = APIClient()
#     client.force_authenticate(user)
#
#     url = reverse("projects-detail", args=[project.id])
#     response = client.patch(url, data={"unknown": "UNKNOWN"})
#
#     assert response.status_code == 400


@pytest.mark.django_db
def test_project_simple_user_cannot_update_by_project_patch_api(request, client):
    old_status = "DRAFT"
    new_status = "READY"

    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = baker.make(models.Project, sites=[site], status=old_status)

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("projects-detail", args=[project.id])
    response = client.patch(url, data={"status": new_status})

    assert response.status_code == 403

    project.refresh_from_db()
    assert project.status == old_status


@pytest.mark.django_db
def test_project_is_updated_by_project_patch_api(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = baker.make(models.Project, sites=[site], status="DRAFT")

    utils.assign_advisor(user, project, site)

    new_status = "READY"

    client = APIClient()
    client.force_authenticate(user)

    url = reverse("projects-detail", args=[project.id])
    response = client.patch(url, data={"status": new_status})

    assert response.status_code == 200
    assert response.data["status"] == new_status

    project.refresh_from_db()
    assert project.status == new_status


########################################################################
# user project status list
########################################################################


@pytest.mark.django_db
def test_project_status_needs_authentication():
    client = APIClient()
    url = reverse("userprojectstatus-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_change_some_one_else_project_status(request):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # project and user statuses
    project = baker.make(models.Project, sites=[site])
    baker.make(models.UserProjectStatus, user=user, site=site, project=project)
    baker.make(models.UserProjectStatus, site=site, project=project)
    # FIXME il manque un bout ici ?!?


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects(request):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = baker.make(
        models.Project,
        sites=[site],
        status="READY",
        commune__name="Ma Comune",
        commune__department__name="Mon Departement",
        name="Mon project",
    )
    mine = baker.make(models.UserProjectStatus, user=user, site=site, project=project)

    baker.make(
        models.ProjectSwitchtender, site=site, switchtender=user, project=project
    )
    # a public note with notification for myself
    pub_note = baker.make(models.Note, public=True, project=mine.project)
    verb = verbs.Conversation.PUBLIC_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=pub_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # a private note with notification for someone else
    priv_note = baker.make(models.Note, public=False, project=mine.project)
    verb = verbs.Conversation.PRIVATE_MESSAGE
    notify.send(
        sender=user,
        recipient=baker.make(auth_models.User),  # for someone else
        verb=verb,
        action_object=priv_note,
        target=project,
        public=False,  # only appear on crm stream
    )

    # another one not for me
    other = baker.make(models.UserProjectStatus, site=site)  # noqa

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("userprojectstatus-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["id"] == mine.id
    assert first["project"]["id"] == mine.project.id

    assert len(first["project"]["switchtenders"]) == 1
    switchtender = first["project"]["switchtenders"][0]
    assert switchtender["email"] == user.email

    # user project status fields
    assert set(first.keys()) == set(["id", "project", "status"])

    # project fields: not ideal
    expected = [
        "commune",
        "created_on",
        "id",
        "inactive_since",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
        "status",
        "switchtenders",
        "updated_on",
    ]
    assert set(first["project"].keys()) == set(expected)
    assert first["project"]["is_switchtender"] is True
    assert first["project"]["is_observer"] is False
    assert first["project"]["notifications"] == {
        "count": 1,
        "has_collaborator_activity": True,
        "new_recommendations": 0,
        "unread_private_messages": 0,
        "unread_public_messages": 1,
        "project_id": str(project.id),
    }


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects_for_site(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    local = baker.make(models.UserProjectStatus, user=user, site=site)
    other = baker.make(models.UserProjectStatus, user=user)  # noqa

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["id"] == local.id
    assert first["project"]["id"] == local.project.id


@pytest.mark.django_db
def test_user_project_status_dont_list_unmoderated_projects_for_regional_advisors(
    request,
):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
        status="DRAFT",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(reverse("userprojectstatus-list"))

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_advisor_access_new_regional_project_status(request):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
        status="TO_PROCESS",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["project"]["id"] == project.id


@pytest.mark.django_db
def test_advisor_access_makes_no_user_project_status_duplicate(request):
    project = baker.make(
        models.Project,
        sites=[get_current_site(request)],
        commune__department__code="01",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    baker.make(
        models.UserProjectStatus,
        project=project,
        site=get_current_site(request),
        user=user,
    )

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = client.get(url)

    assert response.status_code == 200
    assert response.data["count"] == 1

    first = response.data["results"][0]
    assert first["project"]["id"] == project.id


########################################################################
# user project status detail
########################################################################


@pytest.mark.django_db
def test_project_status_detail_needs_authentication(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("userprojectstatus-detail", args=[project.id])
    response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_detail_signals_unknown_object(request):
    user = baker.make(auth_models.User)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[0])
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_cannot_access_other_user_project_status(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    other = baker.make(models.UserProjectStatus, site=site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[other.id])
    response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_access_my_user_project_status(request):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    mine = baker.make(models.UserProjectStatus, user=user, site=site)

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[mine.id])
    response = client.get(url)

    assert response.status_code == 200
    ups = response.data
    assert ups["id"] == mine.id
    assert ups["project"]["id"] == mine.project.id


########################################################################
# user project status patch
########################################################################


@pytest.mark.django_db
def test_project_status_patch_needs_authentication(request):
    site = get_current_site(request)
    project = baker.make(models.Project, sites=[site])

    client = APIClient()

    url = reverse("userprojectstatus-detail", args=[project.id])
    response = client.patch(url, data={"status": "DONE"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_patch_dont_update_others_object(request):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, site=site, status="DRAFT")

    new_status = "DONE"

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = client.patch(url, data={"status": new_status})

    assert response.status_code == 404

    # object is updated
    ups.refresh_from_db()
    assert ups.status == "DRAFT"


@pytest.mark.django_db
def test_project_status_patch_updates_object_and_log(request):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, user=user, site=site, status="DRAFT")

    new_status = "DONE"

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = client.patch(url, data={"status": new_status})

    # response is ok with new content
    assert response.status_code == 200
    updated_ups = response.data
    assert updated_ups["status"] == new_status

    # object is updated
    ups.refresh_from_db()
    assert ups.status == new_status

    # update is logged
    stream = user_stream(user, with_user_activity=True)
    assert stream.count() == 1
    assert stream[0].verb == verbs.Project.USER_STATUS_UPDATED


########################################################################
# REST API: searching topics
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_topic_api(client):
    url = reverse("topics-list")
    response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_cannot_search_topic_api(client, request):
    current_site = get_current_site(request)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    project = baker.make(models.Project)
    topic.projects.add(project)

    url = reverse("topics-list")
    response = client.get(url, {"search": "acme"}, format="json")

    assert response.status_code == 403


@pytest.mark.django_db
def test_unused_topics_are_not_suggested_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    baker.make(models.Topic, name="acme topic", site=current_site)

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acme", "restrict_to": "projects"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_topics_on_deleted_task_are_not_suggested_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    task = baker.make(tasks_models.Task, deleted=timezone.now())
    topic.tasks.add(task)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acm topc", "restrict_to": "recommendations"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_topics_on_deleted_project_are_not_suggested_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    project = baker.make(models.Project, deleted=timezone.now())
    topic.projects.add(project)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acm topc", "restrict_to": "projects"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_projects_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    task = baker.make(tasks_models.Task)
    topic.tasks.add(task)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acm topc", "restrict_to": "projects"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_recommendations_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    project = baker.make(models.Project)
    topic.projects.add(project)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acm topc", "restrict_to": "recommendations"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_nonexistent_via_rest_api(request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)

    baker.make(models.Topic, name="acme topic", site=current_site)

    response = client.get(
        reverse("topics-list"),
        data={"search": "acme topic", "restrict_to": "gne"},
        format="json",
    )

    assert response.status_code == 200
    assert len(response.data["results"]) == 0


# eof
