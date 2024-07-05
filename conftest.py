# global personal configuration of pytest
import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from model_bakery import baker

from recoco.apps.projects.models import Project


# -- Global Fixtures
@pytest.fixture(scope="session", autouse=True)
def setup_db(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("update_permissions")


# -- Project Fixtures
@pytest.fixture
def make_project():
    def _make_project(site, status="READY", **kwargs):
        project = baker.make(Project, **kwargs)
        if site:
            project.project_sites.create(site=site, status=status, is_origin=True)

        return project

    return _make_project


@pytest.fixture
def project_draft(request, make_project):
    """Create a project on the current site with status PROPOSED"""
    site = get_current_site(request)
    yield make_project(site=site, status="DRAFT")


@pytest.fixture
def project_proposed(request, make_project):
    """Create a project on the current site with status PROPOSED"""
    site = get_current_site(request)
    yield make_project(site=site, status="PROPOSED")


@pytest.fixture
def project(request, make_project):
    """Create a project on the current site with status READY"""
    site = get_current_site(request)
    yield make_project(site=site, status="READY")


project_ready = project


# eof
