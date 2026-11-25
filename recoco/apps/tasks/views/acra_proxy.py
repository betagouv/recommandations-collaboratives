# encoding: utf-8

import logging

import requests
import sentry_sdk
from django.conf import settings
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recoco.apps.projects import models as project_models
from recoco.utils import has_perm

logger = logging.getLogger(__name__)


def _acra_headers():
    token = getattr(settings, "ACRA_API_TOKEN", None)
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _acra_url(path):
    base = settings.ACRA_API_BASE_URL.rstrip("/")
    return f"{base}{path}"


class CanManageTasks(BasePermission):
    def has_permission(self, request, view):
        project = get_object_or_404(
            project_models.Project, sites=request.site, pk=view.kwargs["project_id"]
        )
        return has_perm(request.user, "projects.manage_tasks", project)


class AcraAskView(APIView):
    permission_classes = [IsAuthenticated, CanManageTasks]

    def post(self, request, project_id):
        try:
            response = requests.post(
                _acra_url("/ask"),
                headers=_acra_headers(),
                json=request.data,
                params={"site_id": request.site.id},
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("ACRA /ask request failed")
            sentry_sdk.capture_exception(exc)
            return Response(
                {"detail": "Upstream service unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(response.json())


class AcraCoRecommendationsView(APIView):
    permission_classes = [IsAuthenticated, CanManageTasks]

    def get(self, request, project_id):
        params = [
            ("resource_ids", rid)
            for rid in request.query_params.getlist("resource_ids")
        ]
        params.append(("site_id", request.site.id))

        try:
            response = requests.get(
                _acra_url("/co-recommendations"),
                headers=_acra_headers(),
                params=params,
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            logger.exception("ACRA /co-recommendations request failed")
            sentry_sdk.capture_exception(exc)
            return Response(
                {"detail": "Upstream service unavailable."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(response.json())
