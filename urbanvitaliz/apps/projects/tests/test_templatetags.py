# encoding: utf-8

"""
Tests for project application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-01 10:11:56 CEST
"""


import pytest
from django.contrib.sites.shortcuts import get_current_site
from model_bakery.recipe import Recipe

from .. import models
from ..templatetags import projects_extra

########################################################################
# template tags and filters
########################################################################


@pytest.mark.django_db
def test_current_project_tag(request):
    current_site = get_current_site(request)
    project = Recipe(models.Project, sites=[current_site]).make()
    session = {"project_id": project.id}
    assert projects_extra.current_project(session) == project
