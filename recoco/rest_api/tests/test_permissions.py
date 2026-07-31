from unittest.mock import Mock, PropertyMock, patch

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.sites.models import Site
from django.test.client import RequestFactory
from guardian.shortcuts import assign_perm
from model_bakery import baker

from ..permissions import (
    IsM2MPartner,
    IsStaffForSite,
    IsStaffForSiteOrIsAuthenticatedReadOnly,
    IsStaffForSiteOrReadOnly,
)


@pytest.fixture
def std_request():
    request = RequestFactory()
    user = baker.prepare(User)
    request.user = user
    site = baker.prepare(Site)
    request.site = site
    return request


def test_is_staff_for_site(std_request):
    permission = IsStaffForSite()

    with patch(
        "recoco.rest_api.permissions.is_staff_for_site", Mock(return_value=True)
    ) as mock_is_staff_for_site:
        assert permission.has_permission(std_request, None) is True
        mock_is_staff_for_site.assert_called_once_with(
            user=std_request.user, site=std_request.site
        )

    with patch(
        "recoco.rest_api.permissions.is_staff_for_site", Mock(return_value=False)
    ) as mock_is_staff_for_site:
        assert permission.has_permission(std_request, None) is False
        mock_is_staff_for_site.assert_called_once_with(
            user=std_request.user, site=std_request.site
        )


@pytest.mark.parametrize(
    "request_method,is_staff_return_value,expected_result",
    [
        ("GET", True, True),
        ("GET", False, True),
        ("HEAD", False, True),
        ("OPTIONS", False, True),
        ("POST", True, True),
        ("POST", False, False),
        ("PUT", True, True),
        ("PUT", False, False),
        ("PATCH", True, True),
        ("PATCH", False, False),
        ("DELETE", True, True),
        ("DELETE", False, False),
    ],
)
def test_is_staff_for_site_or_read_only(
    std_request, request_method, is_staff_return_value, expected_result
):
    std_request.method = request_method

    permission = IsStaffForSiteOrReadOnly()

    with patch(
        "recoco.rest_api.permissions.is_staff_for_site",
        Mock(return_value=is_staff_return_value),
    ):
        assert permission.has_permission(std_request, None) is expected_result


@pytest.mark.parametrize(
    "request_method,user_is_authenticated,is_staff_return_value,expected_result",
    [
        ("GET", False, False, False),
        ("HEAD", False, False, False),
        ("OPTIONS", False, False, False),
        ("GET", True, False, True),
        ("HEAD", True, False, True),
        ("OPTIONS", True, False, True),
        ("POST", True, False, False),
        ("POST", True, True, True),
        ("PUT", True, False, False),
        ("PUT", True, True, True),
        ("PATCH", True, False, False),
        ("PATCH", True, True, True),
        ("DELETE", True, False, False),
        ("DELETE", True, True, True),
    ],
)
def test_is_staff_for_site_or_is_authenticated_read_only(
    std_request,
    request_method,
    user_is_authenticated,
    is_staff_return_value,
    expected_result,
):
    std_request.method = request_method

    with (
        patch(
            "django.contrib.auth.models.User.is_authenticated",
            new_callable=PropertyMock,
        ) as mock_is_authenticated,
        patch(
            "recoco.rest_api.permissions.is_staff_for_site"
        ) as mock_is_staff_for_site,
    ):
        mock_is_authenticated.return_value = user_is_authenticated
        mock_is_staff_for_site.return_value = is_staff_return_value

        permission = IsStaffForSiteOrIsAuthenticatedReadOnly()
        assert permission.has_permission(std_request, None) is expected_result


@pytest.mark.django_db
def test_is_m2m_partner():
    site = Site.objects.get_current()
    other_site = baker.make(Site)

    partner = baker.make(User)
    assign_perm("use_m2m_api", partner, site)

    other_partner = baker.make(User)
    assign_perm("use_m2m_api", other_partner, other_site)

    request = RequestFactory().post("/")
    request.site = site

    permission = IsM2MPartner()

    # nobody gets in without an account
    request.user = AnonymousUser()
    assert permission.has_permission(request, None) is False

    # being authenticated is not enough, the permission is required
    request.user = baker.make(User)
    assert permission.has_permission(request, None) is False

    # the permission is held on a site: a partner of another one is a stranger here
    request.user = other_partner
    assert permission.has_permission(request, None) is False

    # our partner holds it on the site being requested
    request.user = partner
    assert permission.has_permission(request, None) is True

    # ... and only opens that very site, not the neighbouring ones
    request.site = other_site
    assert permission.has_permission(request, None) is False
