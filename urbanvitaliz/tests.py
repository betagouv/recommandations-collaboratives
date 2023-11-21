import pytest
from django.conf import settings
from django.shortcuts import reverse
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites_models
from django.contrib.sites.shortcuts import get_current_site
from guardian.shortcuts import assign_perm
from rest_framework.test import APIClient
from model_bakery.recipe import Recipe
from model_bakery import baker

from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.resources import models as resources_models
from urbanvitaliz.utils import login


from . import utils


@pytest.mark.django_db
def test_build_absolute_url():
    url = utils.build_absolute_url("somewhere")

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" not in url


@pytest.mark.django_db
def test_build_absolute_url_with_auto_login():
    user = Recipe(auth.User, username="owner", email="owner@example.com").make()

    url = utils.build_absolute_url("somewhere", user)

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" in url


@pytest.mark.django_db
def test_build_absolute_url_with_empty_auto_login():
    url = utils.build_absolute_url("somewhere", auto_login_user=None)

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "?sesame=" not in url


@pytest.mark.django_db
def test_build_absolute_url_keeps_anchor():
    url = utils.build_absolute_url("somewhere#around-the-rainbow")

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "#around" in url
    assert "?sesame=" not in url


@pytest.mark.django_db
def test_build_absolute_url_with_auto_login_url_keeps_anchor():
    user = Recipe(auth.User, username="owner", email="owner@example.com").make()

    url = utils.build_absolute_url("somewhere#around-the-rainbow", user)

    assert url.startswith("https://")
    assert "/somewhere" in url
    assert "#around" in url
    assert "?sesame=" in url


@pytest.mark.django_db
def test_build_absolute_url_with_auto_login_url_sends_anchor_at_the_end():
    user = Recipe(auth.User, username="owner", email="owner@example.com").make()

    url = utils.build_absolute_url("somewhere#around-the-rainbow", user)

    assert url.endswith("#around-the-rainbow")


@pytest.mark.django_db
def test_has_perm_considers_current_site():
    user = Recipe(auth.User, username="owner", email="owner@example.com").make()
    project = Recipe(projects_models.Project).make()
    site2 = Recipe(sites_models.Site).make()

    perm_name = "projects.use_tasks"

    assign_perm(perm_name, user, project)

    # Should be present on current site
    assert utils.has_perm(user, perm_name, project)

    # Shoudn't be present on another site
    with settings.SITE_ID.override(site2.pk):
        assert not utils.has_perm(user, perm_name, project)


@pytest.mark.django_db
def test_site_staff_bypass_has_perm_for_her_site_objects(client, request):
    project = Recipe(projects_models.Project).make()

    site = get_current_site(request)
    site2 = Recipe(sites_models.Site).make()

    perm_name = "projects.use_tasks"

    with login(client, groups=["example_com_staff"]) as user:
        # Should be present on current site
        with settings.SITE_ID.override(site.pk):
            assert utils.has_perm(user, perm_name, project)

        # Shoudn't be present on another site
        with settings.SITE_ID.override(site2.pk):
            assert not utils.has_perm(user, perm_name, project)


@pytest.mark.django_db
def test_site_staff_bypass_has_perm_for_her_site(client, request):
    site = get_current_site(request)

    perm_name = "sites.list_projects"

    with login(client, groups=["example_com_staff"]) as user:
        # Should be present on current site
        with settings.SITE_ID.override(site.pk):
            assert utils.has_perm(user, perm_name, site)


@pytest.mark.django_db
@pytest.mark.skip
def test_site_staff_cannot_bypass_perm_for_other_site(client, request):
    """
    XXX Currently disabled because we can't find an elegant way to fix this problem
    """
    site = get_current_site(request)
    site2 = Recipe(sites_models.Site).make()

    perm_name = "sites.list_projects"

    with login(client, groups=["example_com_staff"]) as user:
        with settings.SITE_ID.override(site.pk):
            assert not utils.has_perm(user, perm_name, site2)


@pytest.mark.django_db
def test_rest_api_responds_to_xml_content_type(client, request):
    """
    Make sure we can get a XML version of the body by appending ?format=xml
    to the REST API request paths.
    """
    Recipe(
        resources_models.Resource,
        status=resources_models.Resource.PUBLISHED,
        sites=[get_current_site(request)],
        title="A Nice title",
    ).make()
    user = baker.make(auth.User, email="me@example.com")

    client = APIClient()
    client.force_authenticate(user=user)

    url = reverse("resources-list")
    response = client.get(f"{url}?format=xml")

    assert response.status_code == 200
    assert "application/xml" in response.headers["content-type"]
    assert len(response.data) == 1


@pytest.mark.django_db
def test_assign_site_staff(client, request):
    site = get_current_site(request)

    user = baker.make(auth.User)

    utils.assign_site_staff(site, user)

    staff_group = utils.get_group_for_site("staff", site)
    assert user in staff_group.user_set.all()
    assert site in user.profile.sites.all()
