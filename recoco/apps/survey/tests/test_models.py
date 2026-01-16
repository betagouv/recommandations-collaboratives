# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-27 12:06:10 CEST
"""

import pytest
from django.utils import timezone
from model_bakery.recipe import Recipe

from .. import models, utils
from ..models import DIRECTION

########################################################################
# Session
########################################################################


@pytest.mark.django_db
def test_session_next_question_if_none():
    survey = Recipe(models.Survey).make()
    Recipe(models.QuestionSet, survey=survey).make()
    Recipe(models.QuestionSet, survey=survey).make()

    session = Recipe(models.Session, survey=survey).make()

    next_q = session.next_question()
    assert next_q is None


@pytest.mark.django_db
def test_session_next_question_returns_first_a_default():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()
    next_q = session.next_question()

    assert next_q == q1


@pytest.mark.django_db
def test_session_next_question_with_priority():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    Recipe(models.Question, priority=10, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, priority=100, text="Q2", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()
    next_q = session.next_question()

    assert next_q == q2


#
# next question


@pytest.mark.django_db
def test_session_next_question_skips_answered_ones():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()
    q3 = Recipe(models.Question, text="Q3", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()

    # Answer Q2, meaning it should be skipped
    Recipe(models.Answer, session=session, question=q2).make()

    assert session.next_question(q1) == q3


@pytest.mark.django_db
def test_session_next_question_skips_untriggered_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    Recipe(
        models.Question, text="Q2", precondition="oscar-mike", question_set=qs
    ).make()
    q3 = Recipe(models.Question, text="Q3", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()

    assert session.next_question(q1) == q3


@pytest.mark.django_db
def test_session_next_question_skips_untriggered_qs():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey, heading="QS1").make()
    qs2 = Recipe(models.QuestionSet, survey=survey, heading="QS2").make()
    qs2.precondition_tags.set(["oscar-mike"])
    qs3 = Recipe(models.QuestionSet, survey=survey, heading="QS3").make()
    q1 = Recipe(models.Question, text="Q1.1", question_set=qs).make()
    Recipe(models.Question, text="Q2.1", question_set=qs2).make()
    q3 = Recipe(models.Question, text="Q3.1", question_set=qs3).make()

    session = Recipe(models.Session, survey=survey).make()

    assert session.next_question(q1) == q3


#
# previous question


@pytest.mark.django_db
def test_session_previous_question_skips_answered_ones():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()
    q3 = Recipe(models.Question, text="Q3", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()

    # Answer Q2, meaning it should be skipped
    Recipe(models.Answer, session=session, question=q2).make()

    assert session.previous_question(q3) == q1


@pytest.mark.django_db
def test_session_previous_question_skips_untriggered_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    Recipe(
        models.Question, text="Q2", precondition="oscar-mike", question_set=qs
    ).make()
    q3 = Recipe(models.Question, text="Q3", question_set=qs).make()

    session = Recipe(models.Session, survey=survey).make()

    assert session.previous_question(q3) == q1


#
# use of question signals


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


########################################################################
# Question Sets
########################################################################


@pytest.mark.django_db
def test_question_set_next():
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey, priority=20).make()
    qs2 = Recipe(models.QuestionSet, survey=survey, priority=10).make()

    assert qs1.following(DIRECTION.NEXT) == qs2
    assert qs2.following(DIRECTION.NEXT) is None


@pytest.mark.django_db
def test_question_set_previous():
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey, priority=20).make()
    qs2 = Recipe(models.QuestionSet, survey=survey, priority=10).make()

    assert qs2.following(DIRECTION.PREVIOUS) == qs1
    assert qs1.following(DIRECTION.PREVIOUS) is None


@pytest.mark.django_db
def test_question_set_first_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()
    Recipe(models.Question, text="Q2", question_set=qs).make()

    assert qs.extreme_question(DIRECTION.NEXT) == q1


@pytest.mark.django_db
def test_question_set_last_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", question_set=qs).make()  # NOQA
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()

    assert qs.extreme_question(DIRECTION.PREVIOUS) == q2


########################################################################
# Questions
########################################################################


@pytest.mark.django_db
def test_question_next_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, priority=0, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, priority=0, text="Q2", question_set=qs).make()

    assert q2 == q1.following(DIRECTION.NEXT)
    assert q2.following(DIRECTION.NEXT) is None


@pytest.mark.django_db
def test_question_next_question_with_priority():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, text="Q1", priority=300, question_set=qs).make()
    q2 = Recipe(models.Question, text="Q2", question_set=qs).make()
    q3 = Recipe(models.Question, text="Q2", priority=200, question_set=qs).make()

    assert q1.following(DIRECTION.NEXT) == q3
    assert q3.following(DIRECTION.NEXT) == q2


@pytest.mark.django_db
def test_question_previous_question():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, priority=0, text="Q1", question_set=qs).make()
    q2 = Recipe(models.Question, priority=0, text="Q2", question_set=qs).make()

    assert q1 == q2.following(DIRECTION.PREVIOUS)
    assert q1.following(DIRECTION.PREVIOUS) is None


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
def test_question_slug():
    q_set = Recipe(models.QuestionSet).make()

    q = models.Question.objects.create(
        question_set=q_set, text="Description précise de l'Action ?"
    )
    assert q.text_short == ""
    assert q.slug == "description-precise-de-laction"

    q = models.Question.objects.create(
        question_set=q_set,
        text="Description précise de l'Action ?",
        text_short="Description précise",
    )
    assert q.slug == "description-precise"

    q = models.Question.objects.create(
        question_set=q_set,
        text="Description précise de l'Action ?",
        text_short="Description précise",
    )
    assert q.slug == "description-precise-2"

    q.deleted = timezone.now()
    q.save()

    q = models.Question.objects.create(
        question_set=q_set,
        text="Description précise de l'Action ?",
        text_short="Description précise",
    )
    assert q.slug == "description-precise-3"


########################################################################
# Choices
########################################################################


@pytest.mark.django_db
def test_choice_order_follows_priority():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q = Recipe(models.Question, priority=0, text="Q", question_set=qs).make()
    c1 = Recipe(models.Choice, priority=0, text="C1", question=q).make()
    c2 = Recipe(models.Choice, priority=10, text="C2", question=q).make()

    assert list(q.choices.all()) == [c2, c1]


########################################################################
# Utils
########################################################################


@pytest.mark.django_db
def test_compute_qs_with_empty_question_set():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    session = Recipe(models.Session).make()

    assert utils.compute_qs_completion(session, qs) == 0


@pytest.mark.django_db
def test_compute_qs_with_no_answer():
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    Recipe(models.Question, priority=0, text="Q", question_set=qs).make()
    session = Recipe(models.Session).make()

    assert utils.compute_qs_completion(session, qs) == 0


@pytest.mark.django_db
def test_compute_qs_fully_answered():
    survey = Recipe(models.Survey).make()
    session = Recipe(models.Session).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q = Recipe(models.Question, priority=0, text="Q", question_set=qs).make()
    Recipe(models.Answer, session=session, question=q).make()

    assert utils.compute_qs_completion(session, qs) == 100


@pytest.mark.django_db
def test_compute_qs_partially_answered():
    survey = Recipe(models.Survey).make()
    session = Recipe(models.Session).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, priority=0, text="Q", question_set=qs).make()
    Recipe(models.Question, priority=0, text="Q2", question_set=qs).make()
    Recipe(models.Answer, session=session, question=q1).make()

    assert utils.compute_qs_completion(session, qs) == 50
