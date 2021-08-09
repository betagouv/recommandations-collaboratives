# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-27 12:06:10 CEST
"""

import pytest
from django.urls import reverse
from model_bakery.recipe import Recipe
from urbanvitaliz.utils import login

from .. import models


#####
# Session
#####
@pytest.mark.django_db
def test_session_next_question_if_none():
    survey = Recipe(models.Survey).make()
    Recipe(models.QuestionSet, survey=survey).make()
    Recipe(models.QuestionSet, survey=survey).make()

    session = Recipe(models.Session, survey=survey).make()

    next_q = session.next_question()
    assert next_q is None


@pytest.mark.django_db
def test_session_next_question_succeed():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()
    next_q = session.next_question()

    assert next_q == q1


@pytest.mark.django_db
def test_question_precondition_succeeds():
    session = Recipe(models.Session).make()

    signal = "gamma"

    Recipe(models.Answer, session=session, signals=signal).make()

    q = Recipe(models.Question, precondition=signal, text="Q-with-precondition").make()

    assert q.check_precondition(session) is True


@pytest.mark.django_db
def test_question_precondition_fails():
    session = Recipe(models.Session).make()

    q = Recipe(models.Question, precondition="gamma", text="Q-with-precondition").make()

    assert q.check_precondition(session) is False


@pytest.mark.django_db
def test_session_signals_union():
    session = Recipe(models.Session).make()

    signals = ["charlie-mike, pan, pan", "tango-yankee"]
    answers = []
    for signal in signals:
        answers.append(Recipe(models.Answer, session=session, signals=signal).make())

    # Check that each signal from the answers are found in the session
    for answer in answers:
        for tag in answer.tags:
            assert tag.name in session.signals


#####
# Question Sets
#####
@pytest.mark.django_db
def test_question_set_next():
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey).make()
    qs2 = Recipe(models.QuestionSet, survey=survey).make()

    assert qs2 == qs1.next()
    assert qs2.next() is None


@pytest.mark.django_db
def test_question_set_previous():
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey).make()
    qs2 = Recipe(models.QuestionSet, survey=survey).make()

    assert qs1 == qs2.previous()
    assert qs1.previous() is None


######
# Questions
#####


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


@pytest.mark.django_db
def test_answered_question_is_saved_to_session(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()
    Recipe(models.Choice, question=q1, value="nope").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice.value, "comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.value == choice.value
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_question_signals_are_copied_over_answer(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    choice = Recipe(
        models.Choice, question=q1, value="yep", signals="lima-charlie, bravo-zulu"
    ).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice.value})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.signals == choice.signals


@pytest.mark.django_db
def test_answered_question_is_updated_to_session(client):
    """Make sure we update and don't duplicate Answer when answering again"""
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_signals = "oscar-mike"
    my_comment = "this is a comment"

    choice1 = Recipe(
        models.Choice, question=q1, value="nope", signals="november-golf"
    ).make()
    choice2 = Recipe(models.Choice, question=q1, value="yep", signals=my_signals).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": choice1.value})
        client.post(url, data={"answer": choice2.value, "comment": my_comment})

    # Fetch persisted answer
    assert models.Answer.objects.filter(session=session, question=q1).count() == 1

    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.value == choice2.value
    assert answer.comment == my_comment
    assert answer.signals == my_signals


@pytest.mark.django_db
def test_question_redirects_to_next_one(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    q2 = Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        response = client.post(url, data={"answer": choice.value})

    assert response.status_code == 302
    assert response.url == reverse("survey-question-details", args=(session.id, q2.id))
