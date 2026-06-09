# encoding: utf-8

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import models as auth_models
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from recoco.apps.projects import utils as project_utils


@pytest.fixture
def advisor(project):
    user = baker.make(auth_models.User)
    project_utils.assign_advisor(user, project)
    return user


@pytest.fixture
def collaborator(project):
    user = baker.make(auth_models.User)
    project_utils.assign_collaborator(user, project)
    return user


def acra_ask_url(project_id):
    return reverse("tasks-acra-ask", args=[project_id])


def acra_co_reco_url(project_id):
    return reverse("tasks-acra-co-recommendations", args=[project_id])


# ============================================================
# /ask
# ============================================================


@pytest.mark.django_db
def test_acra_ask_requires_authentication(project):
    client = APIClient()
    response = client.post(acra_ask_url(project.id), data={}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_acra_ask_requires_manage_tasks_permission(project, collaborator):
    client = APIClient()
    client.force_authenticate(user=collaborator)
    response = client.post(acra_ask_url(project.id), data={}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_acra_ask_returns_404_for_unknown_project(advisor):
    client = APIClient()
    client.force_authenticate(user=advisor)
    response = client.post(acra_ask_url(99999), data={}, format="json")
    assert response.status_code == 404


@pytest.mark.django_db
def test_acra_ask_proxies_request_to_upstream(project, advisor):
    upstream_payload = {"answer_chunks": [], "citations": [], "found_answer": False}
    mock_response = MagicMock()
    mock_response.json.return_value = upstream_payload
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    client.force_authenticate(user=advisor)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.post", return_value=mock_response
    ) as mock_post:
        response = client.post(
            acra_ask_url(project.id),
            data={"query": "test", "context": "ctx"},
            format="json",
        )

    assert response.status_code == 200
    assert response.data == upstream_payload
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"query": "test", "context": "ctx"}
    assert "site_id" in kwargs["params"]


@pytest.mark.django_db
def test_acra_ask_returns_502_on_upstream_error(project, advisor):
    import requests as req

    client = APIClient()
    client.force_authenticate(user=advisor)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.post",
        side_effect=req.RequestException("upstream down"),
    ):
        response = client.post(acra_ask_url(project.id), data={}, format="json")

    assert response.status_code == 502


# ============================================================
# /co-recommendations
# ============================================================


@pytest.mark.django_db
def test_acra_co_reco_requires_authentication(project):
    client = APIClient()
    response = client.get(acra_co_reco_url(project.id))
    assert response.status_code == 403


@pytest.mark.django_db
def test_acra_co_reco_requires_manage_tasks_permission(project, collaborator):
    client = APIClient()
    client.force_authenticate(user=collaborator)
    response = client.get(acra_co_reco_url(project.id))
    assert response.status_code == 403


@pytest.mark.django_db
def test_acra_co_reco_returns_404_for_unknown_project(advisor):
    client = APIClient()
    client.force_authenticate(user=advisor)
    response = client.get(acra_co_reco_url(99999))
    assert response.status_code == 404


@pytest.mark.django_db
def test_acra_co_reco_proxies_request_to_upstream(project, advisor):
    upstream_payload = {
        "co_recommendations": [{"resource_id": 1, "co_occurrence_score": 0.9}]
    }
    mock_response = MagicMock()
    mock_response.json.return_value = upstream_payload
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    client.force_authenticate(user=advisor)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.get", return_value=mock_response
    ) as mock_get:
        response = client.get(
            acra_co_reco_url(project.id),
            {"resource_ids": [1, 2]},
        )

    assert response.status_code == 200
    assert response.data == upstream_payload
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert ("site_id", project.pk.__class__(project.pk)) or any(
        k == "site_id" for k, _ in kwargs["params"]
    )


@pytest.mark.django_db
def test_acra_co_reco_returns_502_on_upstream_error(project, advisor):
    import requests as req

    client = APIClient()
    client.force_authenticate(user=advisor)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.get",
        side_effect=req.RequestException("upstream down"),
    ):
        response = client.get(acra_co_reco_url(project.id))

    assert response.status_code == 502
