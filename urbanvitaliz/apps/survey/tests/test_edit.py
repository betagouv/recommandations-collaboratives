# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-02 16:24:35 CEST
"""

import pytest
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains
from urbanvitaliz.utils import login

from .. import models


########################################################################
# Survey
########################################################################


@pytest.mark.django_db
def test_survey_detail_contains_question_set(client):
    qs = Recipe(models.QuestionSet).make()
    url = reverse("survey-editor-survey-details", args=(qs.survey_id,))
    with login(client, is_staff=True):
        response = client.get(url)
    detail_url = reverse("survey-editor-question-set-details", args=(qs.id,))
    assertContains(response, detail_url)
    new_url = reverse("survey-editor-question-set-create", args=(qs.survey_id,))
    assertContains(response, detail_url)


# eof
