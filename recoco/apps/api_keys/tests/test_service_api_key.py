from datetime import timedelta

import pytest
from django.contrib.sites.models import Site
from django.db import IntegrityError
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recoco.apps.home.models import UserProfile

from ..authentication import ServiceAPIKeyAuthentication
from ..models import ServiceAPIKey


def make_request(site, header):
    request = RequestFactory().get("/api/")
    request.site = site
    request.META["HTTP_AUTHORIZATION"] = header
    return request


@pytest.fixture
def make_key(service_account, current_site):
    def _make_key(site=None, **kwargs):
        return ServiceAPIKey.objects.create_key(
            name="svc-test", user=service_account, site=site or current_site, **kwargs
        )

    return _make_key


@pytest.mark.django_db
def test_other_authorization_scheme_is_ignored(current_site):
    request = make_request(current_site, "Bearer some.jwt.token")

    assert ServiceAPIKeyAuthentication().authenticate(request) is None


@pytest.mark.django_db
def test_valid_key_authenticates_the_service_account(
    make_key, service_account, current_site
):
    api_key, key = make_key()

    user, auth = ServiceAPIKeyAuthentication().authenticate(
        make_request(current_site, f"Api-Key {key}")
    )

    assert user == service_account
    assert auth == api_key


@pytest.mark.django_db
def test_revoked_key_is_rejected(make_key, current_site):
    api_key, key = make_key()
    api_key.revoked = True
    api_key.save()

    with pytest.raises(AuthenticationFailed):
        ServiceAPIKeyAuthentication().authenticate(
            make_request(current_site, f"Api-Key {key}")
        )


@pytest.mark.django_db
def test_expired_key_is_rejected(make_key, current_site):
    _, key = make_key(expiry_date=timezone.now() - timedelta(days=1))

    with pytest.raises(AuthenticationFailed):
        ServiceAPIKeyAuthentication().authenticate(
            make_request(current_site, f"Api-Key {key}")
        )


@pytest.mark.django_db
def test_key_of_another_site_is_rejected(make_key, current_site):
    other_site = baker.make(Site, domain="autre.example.com")
    _, key = make_key(site=other_site)

    with pytest.raises(AuthenticationFailed):
        ServiceAPIKeyAuthentication().authenticate(
            make_request(current_site, f"Api-Key {key}")
        )


@pytest.mark.django_db
def test_key_of_a_user_who_is_no_longer_a_bot_is_rejected(
    make_key, service_account, current_site
):
    _, key = make_key()
    # a bulk update skips the signal that deletes the keys of non-bot users
    UserProfile.objects.filter(user=service_account).update(is_bot=False)

    with pytest.raises(AuthenticationFailed):
        ServiceAPIKeyAuthentication().authenticate(
            make_request(current_site, f"Api-Key {key}")
        )


@pytest.mark.django_db
def test_endpoint_accepts_a_valid_key(api_client, make_key, service_account):
    _, key = make_key()

    response = api_client.get(
        reverse("auth-check"),
        HTTP_AUTHORIZATION=f"Api-Key {key}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == service_account.id


@pytest.mark.django_db
def test_valid_key_updates_last_login(make_key, service_account, current_site):
    _, key = make_key()
    assert service_account.last_login is None

    ServiceAPIKeyAuthentication().authenticate(
        make_request(current_site, f"Api-Key {key}")
    )

    service_account.refresh_from_db()
    assert service_account.last_login is not None


@pytest.mark.django_db
def test_last_login_is_updated_at_most_once_per_hour(
    make_key, service_account, current_site
):
    _, key = make_key()
    recent = timezone.now() - timedelta(minutes=10)
    service_account.last_login = recent
    service_account.save()

    ServiceAPIKeyAuthentication().authenticate(
        make_request(current_site, f"Api-Key {key}")
    )
    service_account.refresh_from_db()
    assert service_account.last_login == recent

    old = timezone.now() - timedelta(hours=2)
    service_account.last_login = old
    service_account.save()

    ServiceAPIKeyAuthentication().authenticate(
        make_request(current_site, f"Api-Key {key}")
    )
    service_account.refresh_from_db()
    assert service_account.last_login > old


@pytest.mark.django_db
def test_rejected_key_does_not_update_last_login(
    make_key, service_account, current_site
):
    make_key()

    with pytest.raises(AuthenticationFailed):
        ServiceAPIKeyAuthentication().authenticate(
            make_request(current_site, "Api-Key not.a-valid-key")
        )

    service_account.refresh_from_db()
    assert service_account.last_login is None


@pytest.mark.django_db
def test_key_names_are_unique(make_key):
    make_key()

    with pytest.raises(IntegrityError):
        make_key()


class SessionAndKeyView(APIView):
    authentication_classes = [SessionAuthentication, ServiceAPIKeyAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"id": request.user.id})


@pytest.mark.django_db
def test_view_with_its_own_auth_classes_accepts_a_key(
    make_key, service_account, current_site
):
    _, key = make_key()

    response = SessionAndKeyView.as_view()(make_request(current_site, f"Api-Key {key}"))

    assert response.status_code == 200
    assert response.data == {"id": service_account.id}
