import pytest
from django.urls import reverse
from model_bakery import baker

from recoco.apps.crm.models import Note


@pytest.mark.django_db
def test_anonymous_can_not_read_feed(client):
    response = client.get(reverse("crm-feed"))
    assert response.status_code == 401


@pytest.mark.django_db
def test_random_cannot_access_feed(client):
    user = baker.make("User")
    client.force_login(user)
    response = client.get(reverse("crm-feed"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_staff_can_access_feed(client, current_site, staff_user):
    object = baker.make("User")
    notes = baker.make(
        Note, site=current_site, related=object, _fill_optional=["title"], _quantity=5
    )

    client.force_login(staff_user)

    response = client.get(reverse("crm-feed"))

    assert response.status_code == 200
    for note in notes:
        assert note.title in response.text
