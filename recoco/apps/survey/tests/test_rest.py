import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site

from recoco.apps.projects.models import Project
from recoco.apps.projects import utils
from recoco.apps.survey.models import Session, Answer, Question

from model_bakery import baker
from unittest.mock import ANY


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient

    return APIClient()


@pytest.mark.django_db
def test_session_view(request, api_client):
    site = get_current_site(request)
    project = baker.make(Project, sites=[site])
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
def test_session_answers_view(request, api_client):
    site = get_current_site(request)
    project = baker.make(Project, sites=[site])
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
