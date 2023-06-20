# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from . import models
from .serializers import ChallengeSerializer, ChallengeDefinitionSerializer


########################################################################
# REST API
########################################################################
class ChallengeDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChallengeDefinitionSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_url_kwarg = "slug"
    lookup_field = "code"

    def get_queryset(self):
        return models.ChallengeDefinition.objects.all()


class ChallengeView(generics.RetrieveUpdateAPIView):
    """
    API endpoint that allows challenges to be viewed or updated.
    """

    http_method_names = ["patch", "get"]
    serializer_class = ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        definition = get_object_or_404(models.ChallengeDefinition, code=slug)

        challenge, _ = models.Challenge.objects.get_or_create(
            user=request.user, challenge_definition=definition
        )
        data = ChallengeSerializer(challenge).data

        return Response(data=data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        definition = get_object_or_404(models.ChallengeDefinition, code=slug)

        challenge = get_object_or_404(
            models.Challenge, user=request.user, challenge_definition=definition
        )

        challenge.acquired_on = timezone.now()
        challenge.save()

        data = ChallengeSerializer(challenge).data

        return Response(data=data, status=status.HTTP_200_OK)


# eof
