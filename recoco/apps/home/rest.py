# encoding: utf-8

from django.contrib.sites import models as sites_models
from django.http import Http404
from notifications import models as notifications_models
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SiteSerializer


class UserNotificationsMarkOneAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
        except notifications_models.Notification.DoesNotExist as exc:
            raise Http404 from exc

        count = 0
        is_hijacked = getattr(request.user, "is_hijacked", False)

        if not is_hijacked:
            if notification.unread:
                count = 1
                notification.mark_as_read()
            notification.mark_as_sent()

        return Response({"marked_as_read": count}, status=status.HTTP_200_OK)


class UserNotificationsMarkAllAsRead(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        count = 0
        is_hijacked = getattr(request.user, "is_hijacked", False)

        if not is_hijacked:
            count = request.user.notifications.unread().mark_all_as_read()

        return Response({"marked_as_read": count}, status=status.HTTP_200_OK)


# ----
# Site
# ----
class SiteViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Sites
    """

    queryset = sites_models.Site.objects
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]


# eof
