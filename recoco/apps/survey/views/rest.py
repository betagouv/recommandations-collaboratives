from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from recoco.apps.projects.models import Project
from recoco.rest_api.permissions import IsStaffForSite

from ..models import Answer, Question, Session
from ..serializers import AnswerSerializer, QuestionSerializer, SessionSerializer


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
                "choices", "question__choices"
            )
        except Session.DoesNotExist:
            return Answer.objects.none()


class SurveyQuestionsView(ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsStaffForSite]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return (
            Question.objects.filter(question_set__survey__site=self.request.site)
            .order_by("id")
            .distinct()
            .prefetch_related("choices")
        )
