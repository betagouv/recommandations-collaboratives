import pytest
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.views import APIView

from ..authentication import WITH_SERVICE_API_KEY
from ..permissions import IsServiceAPIKey


class BotOnlyView(APIView):
    authentication_classes = WITH_SERVICE_API_KEY
    permission_classes = [IsServiceAPIKey]

    def get(self, request):
        return Response()


def call_view(site, user=None, **headers):
    request = APIRequestFactory().get("/api/", **headers)
    request.site = site
    if user:
        force_authenticate(request, user=user)
    return BotOnlyView.as_view()(request)


@pytest.mark.django_db
def test_service_api_key_is_accepted(current_site, bot_key):
    response = call_view(current_site, HTTP_AUTHORIZATION=f"Api-Key {bot_key}")

    assert response.status_code == 200


@pytest.mark.parametrize("username", ["staff_user", "admin_user", "service_account"])
@pytest.mark.django_db
def test_user_without_service_api_key_is_refused(request, current_site, username):
    response = call_view(current_site, user=request.getfixturevalue(username))

    assert response.status_code == 403


@pytest.mark.django_db
def test_superuser_without_service_api_key_is_refused(current_site):
    superuser = baker.make(auth_models.User, is_superuser=True)

    assert call_view(current_site, user=superuser).status_code == 403


@pytest.mark.django_db
def test_anonymous_is_refused(current_site):
    assert call_view(current_site).status_code == 403


@pytest.mark.django_db
def test_bot_client_is_authenticated_as_the_service_account(
    bot_client, service_account
):
    response = bot_client.get(reverse("auth-check"))

    assert response.status_code == 200
    assert response.json()["id"] == service_account.id
