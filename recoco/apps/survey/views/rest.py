from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination

from recoco.apps.projects.models import Project

from ..models import Answer, Session
from ..serializers import AnswerSerializer, SessionSerializer


class SessionView(ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["project_id"]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        project_ids = Project.on_site.for_user(self.request.user).values_list(
            "id", flat=True
        )
        return Session.objects.filter(project__in=project_ids)


class SessionAnswersView(ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        project_ids = Project.on_site.for_user(self.request.user).values_list(
            "id", flat=True
        )
        try:
            session = Session.objects.get(
                project__in=project_ids, id=self.kwargs["session_id"]
            )
            return session.answers.select_related("question").prefetch_related(
                "choices"
            )
        except Session.DoesNotExist:
            return Answer.objects.none()
