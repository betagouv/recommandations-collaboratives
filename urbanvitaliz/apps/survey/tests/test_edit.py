# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-02 16:24:35 CEST
"""

import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertContains, assertRedirects
from urbanvitaliz.utils import login

from .. import models

########################################################################
# surveys
########################################################################


@pytest.mark.django_db
def test_survey_detail_contains_question_set_links(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-survey-details", args=[qs.survey_id])
    with login(client, groups=["example_com_admin"]):
        response = client.get(url)
    detail_url = reverse("survey-editor-question-set-details", args=[qs.id])
    assertContains(response, f'href="{detail_url}"')
    new_url = reverse("survey-editor-question-set-create", args=[qs.survey_id])
    assertContains(response, f'href="{new_url}"')


########################################################################
# question_set
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_update_links(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, groups=["example_com_admin"]):
        response = client.get(url)
    update_url = reverse("survey-editor-question-set-update", args=[qs.id])
    assertContains(response, f'href="{update_url}"')


#
# create


@pytest.mark.django_db
def test_question_set_create_and_redirect(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-create", args=[survey.id])
    data = {
        "priority": 10,
        "heading": "new heading",
        "subheading": "new sub heading",
        "icon": "an-icon",
    }

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    qs = models.QuestionSet.objects.all()[0]
    assert qs.heading == data["heading"]
    assert qs.subheading == data["subheading"]

    new_url = reverse("survey-editor-question-set-details", args=[qs.id])
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_question_set_create_error(request, client):
    survey = Recipe(models.Survey, site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-create", args=[survey.id])
    data = {}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    assert models.QuestionSet.objects.count() == 0
    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_question_set_update_and_redirect(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-update", args=[qs.id])
    data = {
        "priority": 10,
        "heading": "new heading",
        "subheading": "new sub heading",
        "icon": "an-icon",
    }

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    qs = models.QuestionSet.objects.get(id=qs.id)
    assert qs.heading == data["heading"]
    assert qs.subheading == data["subheading"]

    new_url = reverse("survey-editor-question-set-details", args=[qs.id])
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_question_set_update_error(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-update", args=[qs.id])
    data = {}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    qs = models.QuestionSet.objects.get(id=qs.id)
    assert qs.heading != ""

    assert response.status_code == 200


#
# delete


@pytest.mark.django_db
def test_question_set_delete_and_redirect(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-set-delete", args=[qs.id])

    with login(client, groups=["example_com_admin"]):
        response = client.post(url)

    qs = models.QuestionSet.objects_deleted.get(id=qs.id)
    assert qs.deleted

    new_url = reverse("survey-editor-survey-details", args=[qs.survey_id])
    assertRedirects(response, new_url)


########################################################################
# question
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_question_links(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    question = Recipe(models.Question, question_set=qs).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, groups=["example_com_admin"]):
        response = client.get(url)
    update_url = reverse("survey-editor-question-update", args=[question.id])
    assertContains(response, f'href="{update_url}"')
    create_url = reverse("survey-editor-question-create", args=[qs.id])
    assertContains(response, f'href="{create_url}"')


#
# create


@pytest.mark.django_db
def test_question_create_and_redirect(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-create", args=[qs.id])
    data = {
        "text_short": "short version",
        "text": "the text of the question",
        "priority": 1,
    }

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    question = models.Question.objects.all()[0]
    assert question.text == data["text"]

    new_url = reverse(
        "survey-editor-question-set-details", args=[question.question_set_id]
    )
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_question_create_error(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    url = reverse("survey-editor-question-create", args=[qs.id])
    data = {"text": ""}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    assert models.Question.objects.count() == 0
    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_question_update_and_redirect(request, client):
    question = Recipe(
        models.Question, question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-question-update", args=[question.id])
    data = {
        "text_short": "short version",
        "text": "the text of the question",
        "priority": 0,
    }

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    question = models.Question.objects.get(id=question.id)
    assert question.text == data["text"]

    new_url = reverse(
        "survey-editor-question-set-details", args=[question.question_set_id]
    )
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_question_update_error(request, client):
    question = Recipe(
        models.Question, question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-question-update", args=[question.id])
    data = {"text": ""}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    question = models.Question.objects.get(id=question.id)
    assert question.text != data["text"]

    assert response.status_code == 200


#
# delete


@pytest.mark.django_db
def test_question_delete_and_redirect(request, client):
    question = Recipe(
        models.Question, question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-question-delete", args=[question.id])

    with login(client, groups=["example_com_admin"]):
        response = client.post(url)

    question = models.Question.objects_deleted.get(id=question.id)
    assert question.deleted

    new_url = reverse(
        "survey-editor-question-set-details", args=[question.question_set_id]
    )
    assertRedirects(response, new_url)


########################################################################
# choice
########################################################################


@pytest.mark.django_db
def test_question_set_detail_contains_choice_links(request, client):
    qs = Recipe(models.QuestionSet, survey__site=get_current_site(request)).make()
    question = Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=question).make()
    url = reverse("survey-editor-question-set-details", args=[qs.id])
    with login(client, groups=["example_com_admin"]):
        response = client.get(url)
    update_url = reverse("survey-editor-choice-update", args=[choice.id])
    assertContains(response, f'href="{update_url}"')
    create_url = reverse("survey-editor-choice-create", args=[question.id])
    assertContains(response, f'href="{create_url}"')


#
# create


@pytest.mark.django_db
def test_choice_create_and_redirect(request, client):
    question = Recipe(
        models.Question, question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-choice-create", args=[question.id])
    data = {"value": "some value", "text": "the text of the choice"}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    choice = models.Choice.objects.all()[0]
    assert choice.text == data["text"]
    assert choice.value == data["value"]

    new_url = reverse(
        "survey-editor-question-set-details", args=[question.question_set_id]
    )
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_choice_set_create_error(request, client):
    question = Recipe(
        models.Question, question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-choice-create", args=[question.id])
    data = {"value": "", "text": "some text"}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    assert models.Choice.objects.count() == 0
    assert response.status_code == 200


#
# update


@pytest.mark.django_db
def test_choice_update_and_redirect(request, client):
    choice = Recipe(
        models.Choice, question__question_set__survey__site=get_current_site(request)
    ).make()
    url = reverse("survey-editor-choice-update", args=[choice.id])
    data = {"value": "some value", "text": "the text of the choice"}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    choice = models.Choice.objects.get(id=choice.id)
    assert choice.text == data["text"]
    assert choice.value == data["value"]

    new_url = reverse(
        "survey-editor-question-set-details", args=[choice.question.question_set_id]
    ) + "#q-{0}".format(choice.question.id)
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_choice_update_error(request, client):
    choice = Recipe(
        models.Choice,
        question__question_set__survey__site=get_current_site(request),
    ).make()
    url = reverse("survey-editor-choice-update", args=[choice.id])
    data = {"value": "", "text": "some text"}

    with login(client, groups=["example_com_admin"]):
        response = client.post(url, data=data)

    choice = models.Choice.objects.get(id=choice.id)
    assert choice.text != data["text"]

    assert response.status_code == 200


#
# delete


@pytest.mark.django_db
def test_choice_delete_and_redirect(request, client):
    choice = Recipe(
        models.Choice,
        question__question_set__survey__site=get_current_site(request),
    ).make()
    url = reverse("survey-editor-choice-delete", args=[choice.id])

    with login(client, groups=["example_com_admin"]):
        response = client.post(url)

    choice = models.Choice.objects_deleted.get(id=choice.id)
    assert choice.deleted

    new_url = reverse(
        "survey-editor-question-set-details", args=[choice.question.question_set_id]
    )
    assertRedirects(response, new_url)


# eof
