# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""

from datetime import datetime

import pytest
from actstream.models import user_stream
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from guardian.shortcuts import assign_perm
from model_bakery import baker
from notifications.signals import notify
from pytest_django.asserts import assertContains

from recoco import verbs
from recoco.apps.conversations import models as conversations_models
from recoco.apps.tasks import models as tasks_models
from recoco.utils import login

from .. import models, utils
from ..models import Document
from ..utils import assign_advisor

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
def test_project_list_includes_project_for_advisor(request, client, make_project):
    current_site = get_current_site(request)
    project = make_project(commune__name="Lille", site=current_site, status="READY")
    url = reverse("projects-list")

    with login(client, groups=["example_com_advisor"]):
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_project_for_staff(request, client, project):
    url = reverse("projects-list")

    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assertContains(response, project.name)


@pytest.mark.django_db
def test_project_list_includes_only_projects_in_switchtender_departments(
    request, api_client, make_project
):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = make_project(
        site=site,
        status="READY",
        commune__name="Ma Comune",
        commune__department__code="01",
        commune__department__name="Mon Departement",
        name="Mon project",
    )

    # a public note with notification
    message = baker.make(conversations_models.Message, project=project, posted_by=user)
    verb = verbs.Conversation.POST_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=message,
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

    make_project(  # unwanted project
        site=site,
        status="READY",
        commune__department__code="02",
    )

    utils.assign_advisor(user, project, site)

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    data = response.data[0]

    # project fields: not ideal
    expected = [
        "commune",
        "location",
        "latitude",
        "longitude",
        "created_on",
        "id",
        "inactive_since",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "owner",
        "switchtenders",
        "updated_on",
        "description",
        "project_sites",
        "status",
        "tags",
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


@pytest.mark.django_db
def test_project_list_tags_filter(request, api_client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, is_superuser=True)

    project_1 = baker.make(models.Project, sites=[site])
    project_1.tags.add("tag1", "tag2")

    project_2 = baker.make(models.Project, sites=[site])
    project_2.tags.add("tag3")

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")

    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2

    response = api_client.get(f"{url}?tags=tag1,tag3")
    assert response.status_code == 200
    assert len(response.data) == 2

    response = api_client.get(f"{url}?tags=tag3")
    assert response.status_code == 200
    assert len(response.data) == 1

    response = api_client.get(f"{url}?tags=tag5,tag6")
    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_project_list_last_activity_filter(request, api_client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, is_superuser=True)

    with freeze_time("2025-01-01"):
        baker.make(models.Project, sites=[site])

    with freeze_time("2025-01-10"):
        baker.make(models.Project, sites=[site])

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")

    with freeze_time("2025-01-15"):
        response = api_client.get(f"{url}?last_activity=3")
        assert response.status_code == 200
        assert len(response.data) == 0

        response = api_client.get(f"{url}?last_activity=5")
        assert response.status_code == 200
        assert len(response.data) == 1

        response = api_client.get(f"{url}?last_activity=15")
        assert response.status_code == 200
        assert len(response.data) == 2

        response = api_client.get(f"{url}?last_activity=dummy")
        assert response.status_code == 200
        assert len(response.data) == 2

        response = api_client.get(f"{url}?last_activity=")
        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db
def test_project_list_search_filter_fulltext(request, api_client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, is_superuser=True)

    # useful one
    baker.make(
        models.Project,
        sites=[site],
        name="The super niceproject",
        commune__name="Maville",
        commune__postal="99666",
        commune__insee="AZ37",
    )

    # second one with accent
    baker.make(
        models.Project,
        sites=[site],
        name="Le projet de la vérité",
        commune__name="Bayonne",
        commune__postal="64100",
        commune__insee="64102",
    )

    # honeypot one
    baker.make(
        models.Project,
        sites=[site],
        name="Noise noise noise",
        commune__name="Autreville",
        commune__postal="99333",
        commune__insee="28838",
    )

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")

    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 3

    # project title
    response = api_client.get(f"{url}?search=niceproject")
    assert response.status_code == 200
    assert len(response.data) == 1

    # city name
    response = api_client.get(f"{url}?search=maville")
    assert response.status_code == 200
    assert len(response.data) == 1

    # postcode
    response = api_client.get(f"{url}?search=99666")
    assert response.status_code == 200
    assert len(response.data) == 1

    # insee
    response = api_client.get(f"{url}?search=AZ37")
    assert response.status_code == 200
    assert len(response.data) == 1

    # no result is fine?
    response = api_client.get(f"{url}?search=XIDJISJDI")
    assert response.status_code == 200
    assert len(response.data) == 0

    # unaccent
    response = api_client.get(f"{url}?search=verite")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_project_list_search_filter_departments(request, api_client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, is_superuser=True)

    # useful one
    baker.make(
        models.Project,
        sites=[site],
        name="The super niceproject",
        commune__name="Maville",
        commune__postal="99666",
        commune__insee="AZ37",
        commune__department__code="62",
    )

    # honeypot one
    baker.make(
        models.Project,
        sites=[site],
        name="Noise noise noise",
        commune__name="Autreville",
        commune__postal="99333",
        commune__insee="28838",
        commune__department__code="10",
    )

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")

    response = api_client.get(url)
    assert response.status_code == 200
    assert len(response.data) == 2

    # cumulative query FTS+filter
    response = api_client.get(f"{url}?search=niceproject&departments=62")
    assert response.status_code == 200
    assert len(response.data) == 1

    # Multiple departments
    response = api_client.get(f"{url}?departments=10&departments=62")
    assert response.status_code == 200
    assert len(response.data) == 2

    response = api_client.get(f"{url}?departments=10&departments=33")
    assert response.status_code == 200
    assert len(response.data) == 1

    # No department filter
    response = api_client.get(f"{url}?search=niceproject")
    assert response.status_code == 200
    assert len(response.data) == 1


@pytest.mark.django_db
def test_project_list_search_filter_is_cumulative(request, api_client):
    site = get_current_site(request)
    user = baker.make(auth_models.User, is_superuser=True)

    project_1 = baker.make(models.Project, name="ABC", sites=[site])
    project_1.tags.add("tag1", "tag2")

    api_client.force_authenticate(user=user)

    url = reverse("projects-list")

    response = api_client.get(f"{url}?search=ABC&tags=tag1")
    assert response.status_code == 200
    assert len(response.data) == 1


########################################################################
# get project details
########################################################################


@pytest.mark.django_db
def test_anonymous_cannot_use_project_detail_api(request, api_client, project):
    url = reverse("projects-detail", args=[project.id])
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_simple_user_cannot_use_project_detail_api(request, api_client, make_project):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = create_project_with_notifications(site, user, make_project)

    api_client.force_authenticate(user=user)

    url = reverse("projects-detail", args=[project.id])
    response = api_client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_detail_contains_project_info(request, api_client, make_project):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    project = create_project_with_notifications(site, user, make_project)

    utils.assign_advisor(user, project, site)

    api_client.force_authenticate(user=user)

    url = reverse("projects-detail", args=[project.id])
    response = api_client.get(url)

    assert response.status_code == 200

    data = response.data
    check_project_content(project, data)


def create_project_with_notifications(site, user, make_project):
    """Create a new project with user as advisor and notifications

    To keep in sync with check_project_content
    """
    # my project and details
    project = make_project(
        site=site,
        status="READY",
        commune__name="Ma Comune",
        commune__department__code="01",
        commune__department__name="Mon Departement",
        name="Mon project",
    )

    # a public note with notification
    message = baker.make(conversations_models.Message, project=project, posted_by=user)
    verb = verbs.Conversation.POST_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=message,
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
        "location",
        "latitude",
        "longitude",
        "created_on",
        "id",
        "inactive_since",
        "status",
        "is_observer",
        "is_switchtender",
        "name",
        "notifications",
        "org_name",
        "switchtenders",
        "updated_on",
        "private_message_count",
        "public_message_count",
        "recommendation_count",
        "description",
        "project_sites",
        "tags",
        "is_diagnostic_done",
        "advisors_note",
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
def test_anonymous_cannot_use_project_patch_api(request, api_client, project_draft):
    url = reverse("projects-detail", args=[project_draft.id])
    response = api_client.patch(url, data={"name": "lalala"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_bad_project_is_reported_by_project_patch_api(api_client):
    user = baker.make(auth_models.User, email="me@example.com")

    api_client.force_authenticate(user)

    url = reverse("projects-detail", args=[0])
    response = api_client.patch(url, data={"name": "lalala"})

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
def test_project_simple_user_cannot_update_by_project_patch_api(
    request, api_client, project_draft
):
    user = baker.make(auth_models.User, email="me@example.com")

    api_client.force_authenticate(user)

    url = reverse("projects-detail", args=[project_draft.id])
    response = api_client.patch(url, data={"name": "allala"})

    assert response.status_code == 403

    project_draft.refresh_from_db()
    assert project_draft.project_sites.current().status == "DRAFT"


@pytest.mark.django_db
def test_project_is_updated_by_project_patch_api(request, api_client, project_draft):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")

    utils.assign_advisor(user, project_draft, site)

    new_name = "new name"

    api_client.force_authenticate(user)

    url = reverse("projects-detail", args=[project_draft.id])
    response = api_client.patch(url, data={"name": new_name})

    assert response.status_code == 200
    assert response.data["name"] == new_name

    project_draft.refresh_from_db()
    assert project_draft.name == new_name


################
# Project Site Status
################


@pytest.mark.django_db
def test_list_project_statuses_for_non_moderator(
    request, project, project_draft, api_client
):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    assign_perm("list_projects", user, site)

    api_client.force_authenticate(user=user)

    url = reverse("projects-projectsites-list")
    response = api_client.get(url)

    ps = project.project_sites.current()

    # we are only expecting project and not project_draft
    expected = [
        {
            "id": ps.id,
            "project": ps.project_id,
            "site": ps.site_id,
            "is_origin": ps.is_origin,
            "status": ps.status,
        }
    ]

    assert response.status_code == 200
    assert response.data == expected


@pytest.mark.django_db
def test_list_project_statuses_for_moderators(
    request, project, project_draft, api_client
):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    assign_perm("list_projects", user, site)
    assign_perm("moderate_projects", user, site)

    api_client.force_authenticate(user=user)

    url = reverse("projects-projectsites-list")
    response = api_client.get(url)

    # we are expecting project and project_draft
    expected_ids = set([project.pk, project_draft.pk])
    actual_ids = set(e["project"] for e in response.data)

    assert response.status_code == 200
    assert len(response.data) == 2
    assert actual_ids == expected_ids


@pytest.mark.django_db
def test_project_status_is_updated_by_patch_api(request, api_client, project):
    site = get_current_site(request)
    user = baker.make(auth_models.User, email="me@example.com")
    assign_perm("list_projects", user, site)

    new_status = "DONE"

    api_client.force_authenticate(user)

    ps = project.project_sites.current()

    url = reverse("projects-projectsites-detail", args=[ps.id])
    response = api_client.patch(url, data={"status": new_status})

    assert response.status_code == 204

    project.refresh_from_db()
    assert project.project_sites.current().status == new_status


########################################################################
# user project status list
########################################################################


@pytest.mark.django_db
def test_project_status_needs_authentication(request, api_client):
    url = reverse("userprojectstatus-list")
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_user_cannot_change_some_one_else_project_status(request, project):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # project and user statuses
    baker.make(models.UserProjectStatus, user=user, site=site, project=project)
    baker.make(models.UserProjectStatus, site=site, project=project)
    # FIXME il manque un bout ici ?!?


@pytest.mark.django_db
def test_user_project_status_contains_only_my_projects(
    request, api_client, make_project
):
    user = baker.make(auth_models.User, email="me@example.com")
    site = get_current_site(request)
    # my project and details
    project = make_project(
        site=site,
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
    message = baker.make(conversations_models.Message, project=project, posted_by=user)
    verb = verbs.Conversation.POST_MESSAGE
    notify.send(
        sender=user,
        recipient=user,
        verb=verb,
        action_object=message,
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

    api_client.force_authenticate(user=user)

    url = reverse("userprojectstatus-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1

    first = response.data[0]
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
        "project_sites",
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
def test_user_project_status_contains_only_my_projects_for_site(
    request, api_client, project, make_project
):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    other = baker.make(sites_models.Site, name="other site")
    local = baker.make(models.UserProjectStatus, project=project, user=user, site=site)
    baker.make(models.UserProjectStatus, project=make_project(site=other), user=user)

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 1
    first = response.data[0]
    assert first["id"] == local.id
    assert first["project"]["id"] == local.project.id


@pytest.mark.django_db
def test_user_project_status_dont_list_unmoderated_projects_for_regional_advisors(
    request, api_client, make_project
):
    project = make_project(
        site=get_current_site(request),
        commune__department__code="01",
        status="DRAFT",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = api_client.get(url)

    assert response.status_code == 200
    assert len(response.data) == 0


@pytest.mark.django_db
def test_advisor_access_new_regional_project_status(request, api_client, make_project):
    project = make_project(
        site=get_current_site(request),
        commune__department__code="01",
        status="TO_PROCESS",
    )

    group = auth_models.Group.objects.get(name="example_com_advisor")
    user = baker.make(auth_models.User, groups=[group])
    user.profile.departments.add(project.commune.department)

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = api_client.get(url)

    assert response.status_code == 200
    ups = response.data
    assert len(ups) == 1
    assert ups[0]["project"]["id"] == project.id


@pytest.mark.django_db
def test_advisor_access_makes_no_user_project_status_duplicate(
    request, api_client, make_project
):
    project = make_project(
        site=get_current_site(request),
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

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-list")
    response = api_client.get(url)
    assert response.status_code == 200
    ups = response.data
    assert len(ups) == 1
    assert ups[0]["project"]["id"] == project.id


########################################################################
# user project status detail
########################################################################


@pytest.mark.django_db
def test_project_status_detail_needs_authentication(request, api_client, project):
    url = reverse("userprojectstatus-detail", args=[project.id])
    response = api_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_detail_signals_unknown_object(request, api_client):
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[0])
    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_cannot_access_other_user_project_status(request, api_client):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    other = baker.make(models.UserProjectStatus, site=site)

    api_client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[other.id])
    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_access_my_user_project_status(request, api_client, project):
    user = baker.make(auth_models.User)
    site = get_current_site(request)
    mine = baker.make(models.UserProjectStatus, project=project, user=user, site=site)

    api_client.force_authenticate(user=user)

    url = reverse("userprojectstatus-detail", args=[mine.id])
    response = api_client.get(url)

    assert response.status_code == 200
    ups = response.data
    assert ups["id"] == mine.id
    assert ups["project"]["id"] == mine.project.id


########################################################################
# user project status patch
########################################################################


@pytest.mark.django_db
def test_project_status_patch_needs_authentication(request, api_client, project):
    url = reverse("userprojectstatus-detail", args=[project.id])
    response = api_client.patch(url, data={"status": "DONE"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_project_status_patch_dont_update_others_object(request, api_client):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(models.UserProjectStatus, site=site, status="DRAFT")

    new_status = "DONE"

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = api_client.patch(url, data={"status": new_status})

    assert response.status_code == 404

    # object is updated
    ups.refresh_from_db()
    assert ups.status == "DRAFT"


@pytest.mark.django_db
def test_project_status_patch_updates_object_and_log(request, api_client, project):
    user = baker.make(auth_models.User, username="Bob")
    site = get_current_site(request)
    ups = baker.make(
        models.UserProjectStatus, project=project, user=user, site=site, status="DRAFT"
    )

    new_status = "DONE"

    api_client.force_authenticate(user=user)
    url = reverse("userprojectstatus-detail", args=[ups.id])
    response = api_client.patch(url, data={"status": new_status})

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
def test_unused_topics_are_not_suggested_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    baker.make(models.Topic, name="acme topic", site=current_site)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acme", "restrict_to": "projects"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


@pytest.mark.django_db
def test_topics_on_deleted_task_are_not_suggested_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    task = baker.make(tasks_models.Task, deleted=timezone.now())
    topic.tasks.add(task)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acm topc", "restrict_to": "recommendations"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


@pytest.mark.django_db
def test_topics_on_deleted_project_are_not_suggested_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    project = baker.make(models.Project, deleted=timezone.now())
    topic.projects.add(project)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acm topc", "restrict_to": "projects"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_projects_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    task = baker.make(tasks_models.Task)
    topic.tasks.add(task)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acm topc", "restrict_to": "projects"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_recommendations_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    topic = baker.make(models.Topic, name="acme topic", site=current_site)
    project = baker.make(models.Project)
    topic.projects.add(project)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acm topc", "restrict_to": "recommendations"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


@pytest.mark.django_db
def test_topics_are_restricted_to_nonexistent_via_rest_api(request, api_client):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    api_client.force_authenticate(user=user)

    baker.make(models.Topic, name="acme topic", site=current_site)

    url = reverse("topics-list")
    response = api_client.get(
        url, {"search": "acme topic", "restrict_to": "gne"}, format="json"
    )

    assert response.status_code == 200
    assert len(response.data.get("results")) == 0


########################################################################
# REST API: document upload
########################################################################


@pytest.mark.django_db
def test_doc_upload(project_ready, project_editor, client):
    url = reverse("projects-documents-list", args=[project_ready.pk])

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    client.force_login(project_editor)
    res = client.post(url, data)

    assert res.status_code == 201
    assert res.data["id"] is not None
    assert Document.objects.filter(pk=res.data["id"]).exists()
    # send signal..?


@pytest.mark.django_db
def test_doc_upload_does_not_accept_malicious_files(
    client, request, project_ready, project_editor
):
    url = reverse("projects-documents-list", args=[project_ready.id])

    my_file = SimpleUploadedFile(
        "doc.html", b"<html>file_content</html>", content_type="text/html"
    )
    data = {"description": "this is some content", "the_file": my_file}

    client.force_login(project_editor)
    response = client.post(url, data=data)

    assert response.status_code == 400

    assert models.Document.objects.count() == 0


@pytest.mark.django_db
def test_doc_upload_does_not_accept_malicious_files_detects_html(
    client, request, project_ready, project_editor
):
    url = reverse("projects-documents-list", args=[project_ready.id])

    my_file = SimpleUploadedFile(
        "doc.html", b"Blah <script></script>", content_type="text/html"
    )
    data = {"description": "this is some content", "the_file": my_file}

    client.force_login(project_editor)
    response = client.post(url, data=data)

    assert response.status_code == 400

    assert models.Document.objects.count() == 0


@pytest.mark.django_db
def test_doc_upload_does_not_accept_malicious_files_by_extension(
    client, request, project_ready, project_editor
):
    url = reverse("projects-documents-list", args=[project_ready.id])

    my_file = SimpleUploadedFile(
        "doc.html", b"simple plain text", content_type="text/html"
    )
    data = {"description": "this is some content", "the_file": my_file}

    client.force_login(project_editor)
    response = client.post(url, data=data)

    assert response.status_code == 400

    assert models.Document.objects.count() == 0


@pytest.fixture
def inactive_project(request, make_project):
    yield make_project(inactive_since=datetime.today())


@pytest.mark.django_db
def test_doc_upload_reactivates_project(project_editor, inactive_project, client):
    url = reverse("projects-documents-list", args=[inactive_project.pk])
    inactive_project.members.add(project_editor)
    assign_perm("projects.view_public_notes", project_editor, inactive_project)
    assign_perm("projects.use_public_notes", project_editor, inactive_project)

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    client.force_login(project_editor)
    res = client.post(url, data)

    assert res.status_code == 201
    inactive_project.refresh_from_db()
    assert inactive_project.inactive_since is None


@pytest.mark.django_db
def test_doc_upload_by_advisors_lets_projects_unactivated(
    current_site, project_editor, inactive_project, client
):
    url = reverse("projects-documents-list", args=[inactive_project.pk])
    assign_advisor(project_editor, inactive_project)
    assign_perm("projects.view_public_notes", project_editor, inactive_project)
    assign_perm("projects.use_public_notes", project_editor, inactive_project)

    png = SimpleUploadedFile("img.png", b"file_content", content_type="image/png")
    data = {"description": "this is some content", "the_file": png}

    client.force_login(project_editor)
    res = client.post(url, data)

    assert res.status_code == 201
    inactive_project.refresh_from_db()
    assert inactive_project.inactive_since is not None


# eof
