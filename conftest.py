# global personal configuration of pytest
import pytest
from django.contrib.auth import models as auth_models
from django.contrib.auth.models import Group, User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework.test import APIClient

from recoco.apps.projects.models import Project


# -- Global Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("update_permissions")


@pytest.fixture(scope="session", autouse=True)
def create_site_alias(django_db_setup, django_db_blocker):
    from multisite.models import Alias

    with django_db_blocker.unblock():
        site = Site.objects.filter(domain="example.com").first()
        Alias.objects.get_or_create(site=site, domain="example.com", is_canonical=True)


@pytest.fixture(scope="function")
def api_client():
    return APIClient()


@pytest.fixture
def current_site():
    return Site.objects.filter(domain="example.com").first()


@pytest.fixture
def staff_user(current_site):
    staff = baker.make(User)
    staff.profile.sites.add(current_site)
    gstaff = Group.objects.get(name="example_com_staff")
    staff.groups.add(gstaff)
    return staff


# -- Project Fixtures
@pytest.fixture
def make_project(request):
    def _make_project(site=None, status="READY", **kwargs):
        default_data = {
            "description": "Super description",
            "location": "SomeWhere",
        }

        default_data.update(**kwargs)

        project = baker.make(Project, **default_data)
        if not site:
            site = get_current_site(request)

        project.project_sites.create(site=site, status=status, is_origin=True)

        return project

    return _make_project


@pytest.fixture
def project_draft(request, make_project):
    """Create a project on the current site with status PROPOSED"""
    yield make_project(status="DRAFT")


@pytest.fixture
def project_proposed(request, make_project):
    """Create a project on the current site with status PROPOSED"""
    yield make_project(status="PROPOSED")


@pytest.fixture
def project(request, make_project):
    """Create a project on the current site with status READY"""
    yield make_project(status="READY")


project_ready = project


@pytest.fixture()
def project_reader(project_ready):
    project_reader = baker.make(auth_models.User)
    assign_perm("projects.view_public_notes", project_reader, project_ready)
    return project_reader


@pytest.fixture()
def project_editor(project_ready):
    project_editor = baker.make(auth_models.User)
    assign_perm("projects.view_public_notes", project_editor, project_ready)
    assign_perm("projects.use_public_notes", project_editor, project_ready)
    return project_editor


# eof
