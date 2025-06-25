# encoding: utf-8

"""
Rest for ML application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2025-06-25 11:56:20 CEST
"""

import logging

from rest_framework import permissions, viewsets

from . import models
from .serializers import SummarySerializer

logger = logging.getLogger(__name__)


class SummaryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for summaries
    """

    queryset = models.Summary.objects
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SummarySerializer
