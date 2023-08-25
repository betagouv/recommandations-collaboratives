# encoding: utf-8

"""
Rest api for training

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""


from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from . import models, serializers, utils


########################################################################
# REST API
########################################################################


class ChallengeDefinitionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows challenge defintions to be viewed.
    """

    http_method_names = ["get"]
    serializer_class = serializers.ChallengeDefinitionSerializer
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
    serializer_class = serializers.ChallengeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        challenge = utils.get_challenge_for(request.user, codename=slug)
        data = serializers.ChallengeSerializer(challenge).data if challenge else {}

        return Response(data=data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        challenge = utils.get_challenge_for(request.user, codename=slug)

        if not challenge:
            raise Http404()

        if "started_on" in request.data:
            challenge.started_on = timezone.now()
        if "acquired_on" in request.data:
            challenge.acquired_on = timezone.now()
        challenge.save()

        data = serializers.ChallengeSerializer(challenge).data

        return Response(data=data, status=status.HTTP_200_OK)


# eof
