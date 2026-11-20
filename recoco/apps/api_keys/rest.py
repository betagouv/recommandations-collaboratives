from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import ServiceAPIKeyAllowedMixin


class AuthCheckView(ServiceAPIKeyAllowedMixin, APIView):
    """Let a client (e.g. a robot using a service API key) check that its
    credentials are accepted: 200 when authenticated, 403 otherwise."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses=inline_serializer(
            name="AuthCheck",
            fields={
                "id": serializers.IntegerField(),
                "username": serializers.CharField(),
            },
        )
    )
    def get(self, request):
        return Response({"id": request.user.id, "username": request.user.username})
