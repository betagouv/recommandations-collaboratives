# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from rest_framework import viewsets

from . import models
from .serializers import ChallengeSerializer


########################################################################
# REST API
########################################################################
class ChallengeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows challenges to be viewed or edited.
    """

    def get_queryset(self):
        return models.Challenge.objects.all().order_by("id")

    serializer_class = ChallengeSerializer


# eof
