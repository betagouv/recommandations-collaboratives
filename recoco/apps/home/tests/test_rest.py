import pytest

from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker
from notifications.signals import notify
from rest_framework.test import APIClient

from recoco.apps.projects import models as project_models


@pytest.mark.django_db
def test_user_notifications_mark_all_as_read(request):

    site = get_current_site(request)
    project = baker.make(project_models.Project, sites=[site])

    user = baker.make(auth_models.User)
    other_user = baker.make(auth_models.User)

    for verb in ["a fake verb", "other fake verb"]:
        notify.send(sender=user, recipient=user, verb=verb, target=project)
        notify.send(sender=other_user, recipient=other_user, verb=verb, target=project)

    assert user.notifications.unread().count() == 2
    assert other_user.notifications.unread().count() == 2

    client = APIClient()
    client.force_authenticate(user=user)
    url = reverse("notifications-mark-all-as-read")
    response = client.post(url)

    assert response.status_code == 200
    assert response.data["marked_as_read"] == 2
    assert user.notifications.unread().count() == 0
    assert other_user.notifications.unread().count() == 2


# eof
