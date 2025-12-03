# encoding: utf-8

"""
Tests for survey application

authors: guillaume.libersat@beta.gouv.fr
created: 2024-09-24 15:00:10 CEST
"""

import pytest
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery import baker

from recoco.apps.home import models as home_models
from recoco.apps.projects.utils import assign_collaborator
from recoco.utils import login

from .. import models


@pytest.mark.django_db
@pytest.mark.multisite
def test_additional_survey_session_is_created(request, client, project):
    main_site = get_current_site(request)
    another_site = baker.make(Site, name="Another Site")

    main_survey = baker.make(models.Survey, site=main_site)
    another_survey = baker.make(models.Survey, site=another_site)

    baker.make(
        home_models.SiteConfiguration,
        site=main_site,
        project_survey=main_survey,
    )

    baker.make(
        home_models.SiteConfiguration,
        site=another_site,
        project_survey=another_survey,
    )

    project.sites.add(another_site)

    url = reverse("survey-project-session", args=(project.id, another_site.id))
    with login(client, is_staff=False) as user:
        assign_collaborator(user, project)
        response = client.get(url)

    assert response.status_code == 302

    new_session = models.Session.objects.get(survey=another_survey, project=project)
    assert response.url == reverse("survey-session-start", args=(new_session.id,))

    assert models.Session.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.multisite
def test_additional_survey_session_not_created_if_not_on_site_using_it(
    request, client, project
):
    main_site = get_current_site(request)
    another_site = baker.make(Site, name="Another Site")

    main_survey = baker.make(models.Survey, site=main_site)
    another_survey = baker.make(models.Survey, site=another_site)

    baker.make(
        home_models.SiteConfiguration,
        site=main_site,
        project_survey=main_survey,
    )

    baker.make(
        home_models.SiteConfiguration,
        site=another_site,
        project_survey=another_survey,
    )

    url = reverse("survey-project-session", args=(project.id, another_survey.id))
    with login(client, is_staff=False) as user:
        assign_collaborator(user, project)
        response = client.get(url)

    assert response.status_code == 400
    assert models.Session.objects.count() == 0
