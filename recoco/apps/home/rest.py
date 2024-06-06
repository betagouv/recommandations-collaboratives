from django.http import Http404
from notifications import models as notifications_models
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class UserNotificationsMarkOneAsRead(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            notification = request.user.notifications.get(pk=pk)
        except notifications_models.Notification.DoesNotExist:
            raise Http404

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


# eof
