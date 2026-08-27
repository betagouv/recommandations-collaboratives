from datetime import timedelta
from io import StringIO

import pytest
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.test.client import RequestFactory
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework.exceptions import AuthenticationFailed

from ..authentication import ServiceAPIKeyAuthentication
from ..models import ServiceAPIKey


def make_request(site, header):
    request = RequestFactory().get("/api/")
    request.site = site
    request.META["HTTP_AUTHORIZATION"] = header
    return request


@pytest.fixture
def service_account(current_site):
    user = baker.make(User, is_active=True)
    user.profile.sites.add(current_site)
    return user


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
def test_endpoint_accepts_a_valid_key(
    api_client, make_key, service_account, current_site, make_project
):
    _, key = make_key()
    assign_perm("list_projects", service_account, current_site)

    response = api_client.get(
        reverse("projects-detail", args=[make_project().id]),
        HTTP_AUTHORIZATION=f"Api-Key {key}",
    )

    assert response.status_code == 200


@pytest.mark.django_db
def test_command_creates_a_service_account_with_a_working_key(current_site):
    out = StringIO()
    call_command(
        "create_service_account", "svc-grist", site=current_site.domain, stdout=out
    )

    user = User.objects.get(username="svc-grist")
    assert user.has_usable_password() is False
    assert current_site in user.profile.sites.all()

    key = out.getvalue().split("Clé d'API : ")[1].splitlines()[0].strip()
    api_key = ServiceAPIKey.objects.get_from_key(key)

    assert api_key.user == user
    assert api_key.site == current_site
