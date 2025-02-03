import base64

import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
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


# eof
