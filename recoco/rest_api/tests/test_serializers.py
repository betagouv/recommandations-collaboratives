import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from model_bakery import baker
from rest_framework.serializers import ValidationError

from ..serializers import validate_email_for_site


@pytest.mark.django_db
def test_validate_email_for_site_accepts_unknown_email(current_site):
    email = validate_email_for_site("jane@example.com", current_site)

    assert email == "jane@example.com"
    assert not auth_models.User.objects.filter(username="jane@example.com").exists()


@pytest.mark.django_db
def test_validate_email_for_site_accepts_user_of_the_site(current_site, staff_user):
    email = validate_email_for_site(staff_user.username, current_site)

    assert email == staff_user.username


@pytest.mark.django_db
def test_validate_email_for_site_refuses_unavailable_account(current_site):
    user = baker.make(auth_models.User, username="jane@example.com")
    user.profile.sites.add(baker.make(Site))

    with pytest.raises(ValidationError):
        validate_email_for_site("jane@example.com", current_site)
