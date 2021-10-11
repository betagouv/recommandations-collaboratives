# encoding: utf-8

"""
Tests for survey application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-27 12:06:10 CEST
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from model_bakery.recipe import Recipe
from pytest_django.asserts import assertRedirects
from urbanvitaliz.utils import login

from .. import models

#
# answering questions


@pytest.mark.django_db
def test_answered_question_with_comment_only_is_saved_to_session(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_answered_question_with_upload_has_attachment_saved(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    the_file = SimpleUploadedFile("test.pdf", b"Some content.")
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs, upload_title="The upload").make()
    Recipe(models.Question, question_set=qs).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"comment": "blah", "attachment": the_file})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.attachment.size > 0


@pytest.mark.django_db
def test_answered_question_with_single_choice_is_saved_to_session(client):
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
    assert answer.values == choice.value
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_answered_question_with_multiple_choice_is_saved_to_session(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, is_multiple=True, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="a").make()
    Recipe(models.Choice, question=q1, value="b").make()

    my_comment = "this is a comment"
    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": [choice.value], "comment": my_comment})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert answer.values == [choice.value]
    assert answer.comment == my_comment


@pytest.mark.django_db
def test_question_with_comment_only_make_comment_field_mandatory(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={})

    with pytest.raises(models.Answer.DoesNotExist):
        models.Answer.objects.get(session=session, question=q1)


@pytest.mark.django_db
def test_question_with_single_choice_signals_are_copied_over_answer(client):
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
def test_question_with_single_multiple_signals_are_copied_over_answer(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, is_multiple=True, question_set=qs).make()
    Recipe(models.Question, question_set=qs).make()
    c1 = Recipe(
        models.Choice, question=q1, value="a", signals="lima-charlie, bravo-zulu"
    ).make()
    c2 = Recipe(models.Choice, question=q1, value="b", signals="alpha-tango").make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        client.post(url, data={"answer": [c1.value, c2.value]})

    # Fetch persisted answer
    answer = models.Answer.objects.get(session=session, question=q1)
    assert set(answer.signals) == set(f"{c1.signals}, {c2.signals}")


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
    assert answer.values == choice2.value
    assert answer.comment == my_comment
    assert answer.signals == my_signals


@pytest.mark.django_db
def test_question_redirects_to_next_question(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    choice = Recipe(models.Choice, question=q1, value="yep").make()

    url = reverse("survey-question-details", args=(session.id, q1.id))
    with login(client, is_staff=False):
        response = client.post(url, data={"answer": choice.value})

    assert response.status_code == 302
    assert response.url == reverse("survey-question-next", args=(session.id, q1.id))


#
# navigating questions


@pytest.mark.django_db
def test_next_question_redirects_to_next_available_question(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    q2 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q2.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_next_question_redirects_to_done_when_no_more_questions(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    assert response.status_code == 302


@pytest.mark.django_db
def test_next_question_redirects_to_next_question_set(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey, priority=30).make()
    q1 = Recipe(models.Question, question_set=qs1).make()

    qs2 = Recipe(models.QuestionSet, survey=survey, priority=10).make()
    Recipe(models.Question, question_set=qs2).make()

    qs3 = Recipe(models.QuestionSet, survey=survey, priority=20).make()
    q3 = Recipe(models.Question, question_set=qs3).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-next", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q3.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_previous_available_question(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()
    q2 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q2.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q1.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_previous_question_set(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs1 = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs1).make()

    qs2 = Recipe(models.QuestionSet, survey=survey).make()
    q2 = Recipe(models.Question, question_set=qs2).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q2.id))
        response = client.get(url)

    new_url = reverse("survey-question-details", args=(session.id, q1.id))
    assertRedirects(response, new_url)


@pytest.mark.django_db
def test_previous_question_redirects_to_survey_when_not_more_questions(client):
    session = Recipe(models.Session).make()
    survey = Recipe(models.Survey).make()
    qs = Recipe(models.QuestionSet, survey=survey).make()
    q1 = Recipe(models.Question, question_set=qs).make()

    with login(client, is_staff=False):
        url = reverse("survey-question-previous", args=(session.id, q1.id))
        response = client.get(url)

    new_url = reverse("survey-session-details", args=(session.id,))
    assertRedirects(response, new_url)


# eof
