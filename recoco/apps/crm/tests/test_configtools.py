import base64

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker

from recoco.apps.home import models as home_models
from recoco.utils import login


# -- Site configuration
@pytest.mark.django_db
def test_site_configuration_not_available_for_non_admin_users(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-site-configuration")

    with login(client):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_site_configuration_not_available_for_staff_users(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)
    user = baker.make(auth_models.User)

    url = reverse("crm-site-configuration")

    with login(client, user=user, groups=["example_com_staff"]):
        response = client.get(url)

    assert response.status_code == 403


@pytest.mark.django_db
def test_site_configuration_available_for_admin_users(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)
    user = baker.make(auth_models.User)

    url = reverse("crm-site-configuration")
    with login(client, user=user, groups=["example_com_admin"]):
        response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_crm_site_configuration(request, client):
    site = get_current_site(request)
    baker.make(
        home_models.SiteConfiguration,
        site=site,
        sender_email="yyo@yo.com",
        sender_name="Yoo",
        contact_form_recipient="othr@yo.com",
    )

    url = reverse("crm-site-configuration")

    logo_content = base64.b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAUA"
        "AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO"
        "9TXL0Y4OHwAAAABJRU5ErkJggg=="
    )

    logo = SimpleUploadedFile("file.png", logo_content, content_type="image/png")

    with login(client, groups=["example_com_admin"]):
        response = client.post(
            url,
            data={
                "sender_email": "yyo@yo.com",
                "sender_name": "Yoo",
                "contact_form_recipient": "othr@yo.com",
                "reminder_interval": 42,
                "logo_small": logo,
            },
        )

    assert response.status_code == 302


@pytest.mark.django_db
def test_crm_site_configuration_crisp_integration(request, client, settings):
    site = get_current_site(request)
    crisp_token = "a-fake-crisp-token"

    baker.make(
        home_models.SiteConfiguration,
        site=site,
        sender_email="yyo@yo.com",
        sender_name="Yoo",
        contact_form_recipient="othr@yo.com",
        crisp_token=None,
    )

    url = reverse("crm-site-configuration")

    # Crisp should not be active
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert 'data-testid="crisp"' not in str(response.content)

    # Activate crisp by entering a token
    with login(client, groups=["example_com_admin"]):
        response = client.post(
            url,
            data={
                "sender_email": "yyo@yo.com",
                "sender_name": "Yoo",
                "contact_form_recipient": "othr@yo.com",
                "reminder_interval": 42,
                "crisp_token": crisp_token,
            },
        )
        assert response.status_code == 302

    # crisp should now be active on our site
    response = client.get(reverse("home"))
    assert response.status_code == 200
    assert 'data-testid="crisp"' in str(response.content)
    assert crisp_token in str(response.content)


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_requires_login(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-site-configuration-toggle-stopped")
    response = client.post(url, data={"action": "stop"})

    assert response.status_code == 302
    assert "/accounts/login/" in response.url


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_forbidden_for_non_admin_users(
    request, client
):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-site-configuration-toggle-stopped")

    with login(client):
        response = client.post(url, data={"action": "stop"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_forbidden_for_staff_users(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)
    user = baker.make(auth_models.User)

    url = reverse("crm-site-configuration-toggle-stopped")

    with login(client, user=user, groups=["example_com_staff"]):
        response = client.post(url, data={"action": "stop"})

    assert response.status_code == 403


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_only_accepts_post(request, client):
    site = get_current_site(request)
    baker.make(home_models.SiteConfiguration, site=site)

    url = reverse("crm-site-configuration-toggle-stopped")

    with login(client, groups=["example_com_admin"]):
        response = client.get(url)

    assert response.status_code == 405


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_sets_stopped_at(request, client):
    site = get_current_site(request)
    site_configuration = baker.make(
        home_models.SiteConfiguration, site=site, stopped_at=None
    )

    url = reverse("crm-site-configuration-toggle-stopped")

    before = timezone.now()
    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data={"action": "stop"})
    after = timezone.now()

    assert response.status_code == 302
    assert response.url == reverse("crm-site-configuration")

    site_configuration.refresh_from_db()
    assert site_configuration.stopped_at is not None
    assert before <= site_configuration.stopped_at <= after


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_clears_stopped_at(request, client):
    site = get_current_site(request)
    site_configuration = baker.make(
        home_models.SiteConfiguration, site=site, stopped_at=timezone.now()
    )

    url = reverse("crm-site-configuration-toggle-stopped")

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data={"action": "start"})

    assert response.status_code == 302
    assert response.url == reverse("crm-site-configuration")

    site_configuration.refresh_from_db()
    assert site_configuration.stopped_at is None


@pytest.mark.django_db
def test_siteconfiguration_toggle_stopped_clears_when_action_missing(request, client):
    site = get_current_site(request)
    site_configuration = baker.make(
        home_models.SiteConfiguration, site=site, stopped_at=timezone.now()
    )

    url = reverse("crm-site-configuration-toggle-stopped")

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data={})

    assert response.status_code == 302

    site_configuration.refresh_from_db()
    assert site_configuration.stopped_at is None


# eof
