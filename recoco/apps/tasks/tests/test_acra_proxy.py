# encoding: utf-8

from unittest.mock import MagicMock, patch

import pytest
import requests as req
from django.contrib.auth import models as auth_models
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework.test import APIClient


@pytest.fixture
def user_with_manage_tasks(project):
    user = baker.make(auth_models.User)
    assign_perm("projects.manage_tasks", user, project)
    return user


# ============================================================
# Shared access control tests
# ============================================================


@pytest.mark.parametrize(
    "url_name,method",
    [("tasks-acra-ask", "post"), ("tasks-acra-co-recommendations", "get")],
)
@pytest.mark.django_db
def test_acra_requires_authentication(project, url_name, method):
    client = APIClient()
    response = getattr(client, method)(reverse(url_name, args=[project.id]))
    assert response.status_code == 403


@pytest.mark.parametrize(
    "url_name,method",
    [("tasks-acra-ask", "post"), ("tasks-acra-co-recommendations", "get")],
)
@pytest.mark.django_db
def test_acra_requires_manage_tasks_permission(project, url_name, method):
    user = baker.make(auth_models.User)
    client = APIClient()
    client.force_authenticate(user=user)
    response = getattr(client, method)(reverse(url_name, args=[project.id]))
    assert response.status_code == 403


@pytest.mark.parametrize(
    "url_name,method",
    [("tasks-acra-ask", "post"), ("tasks-acra-co-recommendations", "get")],
)
@pytest.mark.django_db
def test_acra_returns_404_for_unknown_project(user_with_manage_tasks, url_name, method):
    client = APIClient()
    client.force_authenticate(user=user_with_manage_tasks)
    response = getattr(client, method)(reverse(url_name, args=[99999]))
    assert response.status_code == 404


@pytest.mark.parametrize(
    "url_name,method,mock_target",
    [
        ("tasks-acra-ask", "post", "recoco.apps.tasks.views.acra_proxy.requests.post"),
        (
            "tasks-acra-co-recommendations",
            "get",
            "recoco.apps.tasks.views.acra_proxy.requests.get",
        ),
    ],
)
@pytest.mark.django_db
def test_acra_returns_502_on_upstream_error(
    project, user_with_manage_tasks, url_name, method, mock_target
):
    client = APIClient()
    client.force_authenticate(user=user_with_manage_tasks)
    with patch(mock_target, side_effect=req.RequestException("upstream down")):
        response = getattr(client, method)(reverse(url_name, args=[project.id]))
    assert response.status_code == 502


# ============================================================
# /ask
# ============================================================


@pytest.mark.django_db
def test_acra_ask_proxies_request_to_upstream(project, user_with_manage_tasks):
    upstream_payload = {"answer_chunks": [], "citations": [], "found_answer": False}
    mock_response = MagicMock()
    mock_response.json.return_value = upstream_payload
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    client.force_authenticate(user=user_with_manage_tasks)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.post", return_value=mock_response
    ) as mock_post:
        response = client.post(
            reverse("tasks-acra-ask", args=[project.id]),
            data={"query": "test", "context": "ctx"},
            format="json",
        )

    assert response.status_code == 200
    assert response.data == upstream_payload
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["json"] == {"query": "test", "context": "ctx"}
    assert "site_id" in kwargs["params"]


# ============================================================
# /co-recommendations
# ============================================================


@pytest.mark.django_db
def test_acra_co_reco_proxies_request_to_upstream(project, user_with_manage_tasks):
    upstream_payload = {
        "co_recommendations": [{"resource_id": 1, "co_occurrence_score": 0.9}]
    }
    mock_response = MagicMock()
    mock_response.json.return_value = upstream_payload
    mock_response.raise_for_status = MagicMock()

    client = APIClient()
    client.force_authenticate(user=user_with_manage_tasks)

    with patch(
        "recoco.apps.tasks.views.acra_proxy.requests.get", return_value=mock_response
    ) as mock_get:
        response = client.get(
            reverse("tasks-acra-co-recommendations", args=[project.id]),
            {"resource_ids": [1, 2]},
        )

    assert response.status_code == 200
    assert response.data == upstream_payload
    mock_get.assert_called_once()
    _, kwargs = mock_get.call_args
    assert ("site_id", project.pk.__class__(project.pk)) or any(
        k == "site_id" for k, _ in kwargs["params"]
    )
