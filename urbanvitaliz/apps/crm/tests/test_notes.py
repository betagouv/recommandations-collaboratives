import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as site_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import login

from .. import models


########################################################################
# create note for user
########################################################################


@pytest.mark.django_db
def test_crm_create_note_user_not_accessible_wo_perm(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("crm-user-note-create", args=[user.id])
    with login(client):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_crm_create_note_user_not_accessible_other_site(request, client):
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
def test_crm_create_note_user_accessible_w_perm(request, client):
    site = get_current_site(request)
    user = baker.make(auth_models.User)
    user.profile.sites.add(site)

    url = reverse("crm-user-note-create", args=[user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_create_note_user_performed(request, client):
    site = get_current_site(request)
    crm_user = baker.make(auth_models.User)
    crm_user.profile.sites.add(site)

    data = {
        "kind": "EMAIL",
        "title": "A note title",
        "content": "A note content",
        "sticky": False,
    }

    url = reverse("crm-user-note-create", args=[crm_user.id])
    with login(client) as user:
        assign_perm("use_crm", user, site)
        response = client.post(url)

    assert response.status_code == 200

    note = models.Note.objects.first()

    assert note.site == site
    assert note.object_id == crm_user.id
    assert note.content == data["content"]


# eof
