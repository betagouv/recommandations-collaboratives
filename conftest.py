# global personal configuration of pytest
import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from model_bakery import baker
from rest_framework.test import APIClient

from recoco.apps.projects.models import Project


# -- Global Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("update_permissions")


@pytest.fixture
def api_client():
    return APIClient


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


# eof
