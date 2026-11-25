import pytest
from allauth.account.models import EmailAddress
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from model_bakery import baker

from recoco.apps.home.utils import (
    UnavailableAccountException,
    find_verified_user_for_site,
    get_or_create_user_for_site,
)

########################################################################
# find user for site
########################################################################


@pytest.mark.django_db
def test_find_verified_user_for_site_returns_none_for_unknown_email(current_site):
    assert find_verified_user_for_site("jane@example.com", current_site) is None


@pytest.mark.parametrize("field", ["username", "email"])
@pytest.mark.django_db
def test_find_verified_user_for_site_returns_user_of_the_site(
    current_site, staff_user, field
):
    setattr(staff_user, field, "Jane@Example.com")
    staff_user.save()

    assert find_verified_user_for_site("jane@example.com", current_site) == staff_user


@pytest.mark.parametrize("field", ["username", "email"])
@pytest.mark.django_db
def test_find_verified_user_for_site_refuses_user_of_another_site(current_site, field):
    user = baker.make(auth_models.User, **{field: "jane@example.com"})
    user.profile.sites.add(baker.make(Site))

    with pytest.raises(UnavailableAccountException):
        find_verified_user_for_site("jane@example.com", current_site)


@pytest.mark.django_db
def test_find_verified_user_for_site_returns_user_with_verified_address(
    current_site, staff_user
):
    baker.make(EmailAddress, user=staff_user, email="jane@example.com", verified=True)

    assert find_verified_user_for_site("Jane@example.com", current_site) == staff_user


@pytest.mark.django_db
def test_find_verified_user_for_site_ignores_unverified_address(
    current_site, staff_user
):
    baker.make(EmailAddress, user=staff_user, email="jane@example.com", verified=False)

    assert find_verified_user_for_site("jane@example.com", current_site) is None


@pytest.mark.django_db
def test_find_verified_user_for_site_refuses_verified_address_of_another_site(
    current_site,
):
    user = baker.make(auth_models.User)
    user.profile.sites.add(baker.make(Site))
    baker.make(EmailAddress, user=user, email="jane@example.com", verified=True)

    with pytest.raises(UnavailableAccountException):
        find_verified_user_for_site("jane@example.com", current_site)


@pytest.mark.django_db
def test_find_verified_user_for_site_refuses_bot(current_site, service_account):
    with pytest.raises(UnavailableAccountException):
        find_verified_user_for_site(service_account.username, current_site)


########################################################################
# get or create user for site
########################################################################


@pytest.mark.django_db
def test_get_or_create_user_for_site_reuses_user_of_the_site(current_site, staff_user):
    user = get_or_create_user_for_site(staff_user.username, current_site)

    assert user == staff_user


@pytest.mark.django_db
def test_get_or_create_user_for_site_creates_user_on_the_site(current_site):
    user = get_or_create_user_for_site("JANE@example.com", current_site)

    assert user.username == "jane@example.com"
    assert user.email == "jane@example.com"
    assert user.has_usable_password() is False
    assert list(user.profile.sites.all()) == [current_site]


@pytest.mark.django_db
def test_get_or_create_user_for_site_does_not_pull_user_of_another_site(current_site):
    user = baker.make(auth_models.User, username="jane@example.com")
    user.profile.sites.add(baker.make(Site))

    with pytest.raises(UnavailableAccountException):
        get_or_create_user_for_site("jane@example.com", current_site)

    assert current_site not in user.profile.sites.all()
