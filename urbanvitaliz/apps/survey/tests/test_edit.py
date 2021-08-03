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
# surveys
########################################################################


@pytest.mark.django_db
def test_survey_detail_contains_question_set_links(client):
    qs = Recipe(models.QuestionSet).make()
    url = reverse("survey-editor-survey-details", args=[qs.survey_id])
    with login(client, is_staff=True):
        response = client.get(url)
    detail_url = reverse("survey-editor-question-set-details", args=[qs.id])
    assertContains(response, f'href="{detail_url}"')
    new_url = reverse("survey-editor-question-set-create", args=[qs.survey_id])
    assertContains(response, f'href="{new_url}"')


########################################################################
# question_set
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_update_links(client):
    qs = Recipe(models.QuestionSet).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, is_staff=True):
        response = client.get(url)
    update_url = reverse("survey-editor-question-set-update", args=[qs.id])
    assertContains(response, f'href="{update_url}"')


########################################################################
# question
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_question_links(client):
    qs = Recipe(models.QuestionSet).make()
    question = Recipe(models.Question, question_set=qs).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, is_staff=True):
        response = client.get(url)
    update_url = reverse("survey-editor-question-update", args=[question.id])
    assertContains(response, f'href="{update_url}"')
    create_url = reverse("survey-editor-question-create", args=[qs.id])
    assertContains(response, f'href="{create_url}"')


########################################################################
# choice
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_choice_links(client):
    qs = Recipe(models.QuestionSet).make()
    question = Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=question).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, is_staff=True):
        response = client.get(url)
    update_url = reverse("survey-editor-choice-update", args=[choice.id])
    assertContains(response, f'href="{update_url}"')
    create_url = reverse("survey-editor-choice-create", args=[question.id])
    assertContains(response, f'href="{create_url}"')


# eof
