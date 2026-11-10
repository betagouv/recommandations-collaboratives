import pytest
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.test.client import RequestFactory
from model_bakery import baker

from ..models import ServiceAPIKey


@pytest.mark.django_db
def test_api_keys_are_read_only_in_admin(current_site):
    bot = baker.make(User, is_active=True)
    bot.profile.is_bot = True
    bot.profile.save()
    api_key, _ = ServiceAPIKey.objects.create_key(
        name="svc", user=bot, site=current_site
    )

    request = RequestFactory().get("/")
    request.user = baker.make(User, is_staff=True, is_superuser=True)
    model_admin = site._registry[ServiceAPIKey]

    assert model_admin.has_view_permission(request, api_key)
    assert not model_admin.has_add_permission(request)
    assert not model_admin.has_change_permission(request, api_key)
    assert not model_admin.has_delete_permission(request, api_key)
