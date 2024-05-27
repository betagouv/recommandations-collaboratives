from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status


class UserNotificationsMarkAllAsRead(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        count = 0
        is_hijacked = getattr(request.user, "is_hijacked", False)

        if not is_hijacked:
            count = request.user.notifications.unread().mark_all_as_read()

        return Response({"marked_as_read": count}, status=status.HTTP_200_OK)


# eof
