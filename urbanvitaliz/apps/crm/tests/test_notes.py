import pytest
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from notifications import notify
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from .. import models

########################################################################
# project create note
########################################################################


@pytest.mark.django_db
def test_crm_project_create_note_not_accessible_for_non_staff(client):
    project = baker.make(projects_models.Project)

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_create_note_not_accessible_other_site(request, client):
    other = baker.make(site_models.Site)

    project = baker.make(projects_models.Project, sites=[other])

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_create_note_accessible_for_staff(request, client):
    site = get_current_site(request)

    project = baker.make(projects_models.Project, sites=[site])

    url = reverse("crm-project-note-create", args=[project.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_create_note(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-project-note-create", args=[project.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


########################################################################
# project update note
########################################################################


@pytest.mark.django_db
def test_crm_project_update_note_not_accessible_for_non_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project)
    note = make_note(project, site)

    url = reverse("crm-project-note-update", args=[project.id, note.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_project_update_note_not_accessible_other_site(request, client):
    other = baker.make(site_models.Site)
    project = baker.make(projects_models.Project, sites=[other])
    note = make_note(project, other)

    url = reverse("crm-project-note-update", args=[project.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_project_update_note_accessible_for_staff(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])
    note = make_note(project, site)

    url = reverse("crm-project-note-update", args=[project.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_project_update_note(request, client):
    site = get_current_site(request)
    project = baker.make(projects_models.Project, sites=[site])
    note = make_note(project, site)

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-project-note-update", args=[project.pk, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


########################################################################
# organization create note
########################################################################


@pytest.mark.django_db
def test_crm_organization_create_note_not_accessible_for_non_staff(client):
    organization = baker.make(addressbook_models.Organization)

    url = reverse("crm-organization-note-create", args=[organization.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organization_create_note_not_accessible_other_site(request, client):
    other = baker.make(site_models.Site)

    organization = baker.make(addressbook_models.Organization, sites=[other])

    url = reverse("crm-organization-note-create", args=[organization.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_organization_create_note_accessible_for_staff(request, client):
    site = get_current_site(request)

    organization = baker.make(addressbook_models.Organization, sites=[site])

    url = reverse("crm-organization-note-create", args=[organization.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_organization_create_note(request, client):
    site = get_current_site(request)
    organization = baker.make(addressbook_models.Organization, sites=[site])

    data = {"content": "hola"}

    url = reverse("crm-organization-note-create", args=[organization.pk])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert note.content == data["content"]


########################################################################
# organization update note
########################################################################


@pytest.mark.django_db
def test_crm_organization_update_note_not_accessible_for_non_staff(request, client):
    site = get_current_site(request)
    organization = baker.make(addressbook_models.Organization)
    note = make_note(organization, site)

    url = reverse("crm-organization-note-update", args=[organization.id, note.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_organization_update_note_not_accessible_other_site(request, client):
    other = baker.make(site_models.Site)
    organization = baker.make(addressbook_models.Organization, sites=[other])
    note = make_note(organization, other)

    url = reverse("crm-organization-note-update", args=[organization.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_organization_update_note_accessible_for_staff(request, client):
    site = get_current_site(request)
    organization = baker.make(addressbook_models.Organization, sites=[site])
    note = make_note(organization, site)

    url = reverse("crm-organization-note-update", args=[organization.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_organization_update_note(request, client):
    site = get_current_site(request)
    organization = baker.make(addressbook_models.Organization, sites=[site])
    note = make_note(organization, site)

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-organization-note-update", args=[organization.pk, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


########################################################################
# create note for user
########################################################################


@pytest.mark.django_db
def test_crm_user_create_note_not_accessible_wo_perm(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("crm-user-note-create", args=[user.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_create_note_not_accessible_other_site(request, client):
    site = get_current_site(request)
    other = baker.make(site_models.Site)
    user = baker.make(auth_models.User)
    user.profile.sites.add(other)

    url = reverse("crm-user-note-create", args=[user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_user_create_note_accessible_w_perm(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("crm-user-note-create", args=[user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_create_note_performed_no_notification(mocker, request, client):
    site = get_current_site(request)
    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(site)

    mocker.patch("notifications.notify.send")

    data = {"content": "A note content"}

    url = reverse("crm-user-note-create", args=[crm_user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    note = models.Note.objects.first()

    assert note.site == site
    assert note.object_id == crm_user.id
    assert note.content == data["content"]

    notify.send.assert_called_once()


@pytest.mark.django_db
def test_crm_user_create_note_notify_if_organization(mocker, request, client):
    site = get_current_site(request)
    crm_user = baker.make(auth_models.User)
    profile = crm_user.profile
    profile.sites.add(site)
    profile.organization = baker.make(addressbook_models.Organization)
    profile.save()

    mocker.patch("notifications.notify.send")

    data = {"content": "A note content"}

    url = reverse("crm-user-note-create", args=[crm_user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url, data=data)

    assert response.status_code == 302

    notify.send.assert_called_once()


########################################################################
# user update note
########################################################################


@pytest.mark.django_db
def test_crm_user_update_note_not_accessible_for_non_staff(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    note = make_note(user, site)

    url = reverse("crm-user-note-update", args=[user.id, note.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_user_update_note_not_accessible_other_site(request, client):
    other = baker.make(site_models.Site)
    user = baker.make(auth_models.User)
    user.profile.sites.add(other)
    note = make_note(user, other)

    url = reverse("crm-user-note-update", args=[user.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_crm_user_update_note_accessible_for_staff(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)
    note = make_note(user, site)

    url = reverse("crm-user-note-update", args=[user.id, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_user_update_note(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)
    note = make_note(user, site)

    data = {"tags": ["canard"], "content": "hola"}

    url = reverse("crm-user-note-update", args=[user.pk, note.id])
    with login(client, groups=["example_com_staff"]):
        response = client.post(url, data)

    assert response.status_code == 302

    note = models.Note.objects.first()
    assert list(note.tags.names()) == data["tags"]


########################################################################
# helpers
########################################################################


def make_note(o, site):
    """Return a note for object o on site"""
    ct = ContentType.objects.get_for_model(o)
    return baker.make(models.Note, content_type=ct, object_id=o.id, site=site)


# eof
