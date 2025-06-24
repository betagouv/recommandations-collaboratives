from unittest.mock import patch

import pytest
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
def test_site_create_permission_required(client):
    """User without permission should receive 403 when accessing site creation."""
    user = baker.make(User)
    client.force_login(user)

    response = client.get(reverse("site-create"))
    assert response.status_code == 403


@pytest.mark.django_db
@patch("recoco.apps.home.views.make_new_site")
def test_site_can_be_created(mock_make_new_site, current_site, client):
    """User with permission can successfully create a site."""
    user = baker.make(User)

    form_data = {
        "name": "My Site",
        "subdomain": "mytestsite",
        "sender_email": "test@example.com",
        "sender_name": "Test Sender",
        "contact_form_recipient": "contact@example.com",
        "legal_address": "123 Salome Street",
    }

    content_type = ContentType.objects.get_for_model(Site)
    perm = Permission.objects.get(codename="add_site", content_type=content_type)
    user.user_permissions.add(perm)
    client.force_login(user)

    response = client.post(reverse("site-create"), data=form_data, follow=True)

    assert response.status_code == 200
    mock_make_new_site.assert_called_once_with(
        name="My Site",
        domain="mytestsite.recoconseil.fr",
        sender_email="test@example.com",
        sender_name="Test Sender",
        contact_form_recipient="contact@example.com",
        legal_address="123 Salome Street",
        admin_user=user,
    )


@pytest.mark.django_db
@patch("recoco.apps.home.views.make_new_site")
def test_duplicate_site_domain_fails(mock_make_new_site, current_site, client):
    """Creating a site with an existing domain raises error and shows message."""
    user = baker.make(User)

    content_type = ContentType.objects.get_for_model(Site)
    perm = Permission.objects.get(codename="add_site", content_type=content_type)
    user.user_permissions.add(perm)
    client.force_login(user)

    mock_make_new_site.side_effect = ValidationError("Domain already exists")

    form_data = {
        "name": "Duplicate Site",
        "subdomain": "existingdomain",
        "sender_email": "dupe@example.com",
        "sender_name": "Duplicate Sender",
        "contact_form_recipient": "contact@dupe.com",
        "legal_address": "456 Salome Street",
    }

    response = client.post(reverse("site-create"), data=form_data, follow=True)

    assert response.status_code == 200
    mock_make_new_site.assert_called_once()
