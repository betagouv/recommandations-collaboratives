from django.db import transaction
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Hit, HitCount
from .serializers import HitInputSerializer


class HitView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (JSONParser,)

    def post(self, request, *args, **kwargs):
        serializer = HitInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not getattr(request.user, "is_hijacked", False):
            with transaction.atomic():
                hitcount, _ = HitCount.objects.get_or_create(
                    site=request.site,
                    **serializer.output_data,
                )
                Hit.objects.create(
                    user=request.user,
                    user_agent=request.headers.get("user-agent", "unknown"),
                    hitcount=hitcount,
                )

        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Hit registered."},
        )
