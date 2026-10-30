# encoding: utf-8

from django.contrib.sites import models as sites_models
from django.http import Http404
from notifications import models as notifications_models
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes as api_permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAuthenticated
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
class SiteViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    API endpoint for Sites
    """

    queryset = sites_models.Site.objects
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated]


# recreate drf answer to call it ourserlves
@api_view(["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"])
@api_permission_classes([AllowAny])  # a 404 must not become a 401/403
def api_not_found(request):
    raise NotFound()


# eof
