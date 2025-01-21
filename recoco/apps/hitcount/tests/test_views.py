import json

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from recoco.apps.addressbook.models import Contact
from recoco.apps.hitcount.models import HitCount
from recoco.apps.hitcount.utils import ct_label
from recoco.apps.tasks.models import Task


@pytest.mark.django_db
def test_hit_view():
    user = baker.make(User)
    contact = baker.make(Contact)
    recommendation = baker.make(Task)

    api_client = APIClient()
    api_client.force_authenticate(user=user)

    url = reverse("api_hit")

    payload = json.dumps(
        {
            "content_object_ct": ct_label(contact),
            "content_object_id": contact.id,
            "context_object_ct": ct_label(recommendation),
            "context_object_id": recommendation.id,
        }
    )

    response = api_client.post(
        path=url,
        headers={"user-agent": "Mozilla/5.0"},
        data=payload,
        content_type="application/json",
    )
    assert response.status_code == 200

    response = api_client.post(
        path=url,
        headers={},
        data=payload,
        content_type="application/json",
    )
    assert response.status_code == 200

    assert HitCount.objects.count() == 1
    hitcount = HitCount.objects.first()
    assert hitcount.hits.count() == 2

    user.is_hijacked = True
    response = api_client.post(
        path=url,
        data=payload,
        content_type="application/json",
    )
    assert response.status_code == 200
    assert HitCount.objects.count() == 1
    assert (
        hitcount.hits.count() == 2
    ), "no hit should be registered when user is hijacked"
