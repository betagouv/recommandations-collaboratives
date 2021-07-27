# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-27 12:06:10 CEST
"""

import pytest
from django.test import TestCase
from model_bakery.recipe import Recipe

from . import models


@pytest.mark.django_db
def test_question_next_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()

    assert q2 == q1.next()
    assert q2.next() is None


@pytest.mark.django_db
def test_question_previous_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()

    assert q1 == q2.previous()
    assert q1.previous() is None
