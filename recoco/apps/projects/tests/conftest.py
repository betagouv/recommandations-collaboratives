import pytest
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from ..models import Project


def make_project(site, status="READY"):
    project = baker.make(Project)
    project.project_sites.create(site=site, status=status, is_origin=True)

    return project


@pytest.fixture
def project_draft(request):
    """Create a project on the current site with status PROPOSED"""
    site = get_current_site(request)
    yield make_project(site=site, status="DRAFT")


@pytest.fixture
def project_proposed(request):
    """Create a project on the current site with status PROPOSED"""
    site = get_current_site(request)
    yield make_project(site=site, status="PROPOSED")


@pytest.fixture
def project(request):
    """Create a project on the current site with status READY"""
    site = get_current_site(request)
    yield make_project(site=site, status="READY")
