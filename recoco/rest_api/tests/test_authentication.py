import jwt
import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker

from recoco.apps.api_keys.models import ServiceAPIKey


@pytest.mark.django_db
def test_obtain_token(client, request):
    user = baker.make(
        get_user_model(),
        email="anakin.skywalker@example.com",
        first_name="Anakin",
        last_name="Skywalker",
    )
    user.set_password("maytheforcebewithyou")
    user.save()

    token_url = reverse("token")
    payload = {
        "username": "anakin.skywalker@example.com",
        "password": "maytheforcebewithyou",
    }

    response = client.post(token_url, data=payload)
    assert response.status_code == 200, response.data
    token = response.json()["access"]

    decoded_token = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=["HS256"],
    )
    assert decoded_token["first_name"] == "Anakin"
    assert decoded_token["last_name"] == "Skywalker"
    assert decoded_token["email"] == "anakin.skywalker@example.com"


@pytest.fixture
def service_account_key(current_site):
    service_account = baker.make(get_user_model(), is_active=True)
    service_account.profile.sites.add(current_site)
    assign_perm("list_projects", service_account, current_site)
    _, key = ServiceAPIKey.objects.create_key(
        name="svc-test", user=service_account, site=current_site
    )
    return service_account, key


@pytest.mark.django_db
def test_api_key_authenticates_on_an_opted_in_endpoint(
    api_client, service_account_key, make_project
):
    service_account, key = service_account_key
    url = reverse("projects-detail", args=[make_project().id])

    assert api_client.get(url).status_code == 403
    assert api_client.get(url, HTTP_AUTHORIZATION="Api-Key nope").status_code == 403

    response = api_client.get(url, HTTP_AUTHORIZATION=f"Api-Key {key}")
    assert response.status_code == 200, response.data
    assert response.wsgi_request.user == service_account


@pytest.mark.django_db
def test_api_key_is_refused_on_endpoints_without_the_mixin(
    api_client, service_account_key
):
    _, key = service_account_key

    response = api_client.get(
        reverse("challenge-definitions-list"), HTTP_AUTHORIZATION=f"Api-Key {key}"
    )

    assert response.status_code == 403
