from unittest.mock import ANY

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery import baker

from recoco.apps.projects import utils
from recoco.apps.survey.models import Answer, Question, Session


@pytest.mark.django_db
def test_session_view(request, api_client, project):
    user = baker.make(User)
    utils.assign_collaborator(user, project)

    session = baker.make(Session, project=project)

    api_client.force_authenticate(user=user)
    response = api_client.get(
        path=reverse("api-survey-sessions"),
    )
    assert response.status_code == 200
    json_response = response.json()

    assert json_response["count"] == 1
    assert json_response["results"][0] == {
        "id": session.id,
        "project": session.project.id,
        "survey": session.survey.id,
    }


@pytest.mark.django_db
def test_session_answers_view(request, api_client, project):
    user = baker.make(User)
    utils.assign_collaborator(user, project)

    session = baker.make(Session, project=project)
    question = baker.make(
        Question,
        text="question text",
        text_short="question text short",
    )
    answer = baker.make(
        Answer,
        session=session,
        question=question,
        comment="My comment",
    )

    api_client.force_authenticate(user=user)
    response = api_client.get(
        path=reverse(
            "api-survey-session-answers",
            kwargs={"session_id": session.id},
        ),
    )
    assert response.status_code == 200
    json_response = response.json()

    assert json_response["count"] == 1
    assert json_response["results"][0] == {
        "id": answer.id,
        "created_on": ANY,
        "updated_on": ANY,
        "question": {
            "id": question.id,
            "text": "question text",
            "text_short": "question text short",
            "slug": "question-text-short",
            "is_multiple": False,
            "choices": [],
        },
        "session": session.id,
        "project": project.id,
        "choices": [],
        "values": [],
        "comment": "My comment",
        "signals": "",
        "updated_by": None,
        "attachment": None,
    }
