import pytest
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_obtain_token(client, request):
    User = get_user_model()
    user = baker.make(User, email="anakin@skywalker.com")
    user.set_password("maytheforcebewithyou")

    current_site = get_current_site(request)
    assert User.objects.filter(profile__sites=current_site).count() == 0

    token_url = reverse("api_token")
    payload = {"username": "anakin@skywalker.com", "password": "maytheforcebewithyou"}

    response = client.post(token_url, data=payload)
    assert response.status_code == 401, response.data

    user.profile.sites.add(current_site)
    assert User.objects.filter(profile__sites=current_site).count() == 1

    response = client.post(token_url, data=payload)
    assert response.status_code == 200, response.data
    assert response.json["token"]
