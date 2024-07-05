import pytest
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from ..models import Project


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
