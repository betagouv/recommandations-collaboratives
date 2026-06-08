# encoding: utf-8

import logging

import requests
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from recoco.apps.projects import models as project_models
from recoco.utils import has_perm_or_403

logger = logging.getLogger(__name__)


def _acra_headers():
    token = getattr(settings, "ACRA_API_TOKEN", None)
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _acra_url(path):
    base = getattr(settings, "ACRA_API_BASE_URL", "").rstrip("/")
    return f"{base}{path}"


class AcraAskView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(
            project_models.Project, sites=request.site, pk=project_id
        )
        has_perm_or_403(request.user, "projects.manage_tasks", project)

        try:
            response = requests.post(
                _acra_url("/ask"),
                headers=_acra_headers(),
                json=request.data,
                params={"site_id": request.site.id},
                timeout=60,
            )
            response.raise_for_status()
        except requests.RequestException:
            logger.exception("ACRA /ask request failed")
            return Response({"error": "Upstream service unavailable."}, status=502)

        return Response(response.json())


class AcraCoRecommendationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id):
        project = get_object_or_404(
            project_models.Project, sites=request.site, pk=project_id
        )
        has_perm_or_403(request.user, "projects.manage_tasks", project)

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
        except requests.RequestException:
            logger.exception("ACRA /co-recommendations request failed")
            return Response({"error": "Upstream service unavailable."}, status=502)

        return Response(response.json())
