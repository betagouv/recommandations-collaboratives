import pytest
from django.conf import settings
from django.contrib.auth import models as auth
from django.contrib.sites import models as sites_models
from django.contrib.sites.shortcuts import get_current_site
from guardian.shortcuts import assign_perm
from model_bakery.recipe import Recipe

from urbanvitaliz.apps.projects import models as projects_models
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
def test_site_staff_bypass_has_perm_for_her_site(client, request):
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
