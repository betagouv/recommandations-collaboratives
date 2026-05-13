from django_filters import ModelChoiceFilter
from django_filters import rest_framework as filters_drf
from rest_framework.generics import ListAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from recoco.apps.projects.filters import request_show_deleted_projects
from recoco.apps.projects.models import Project
from recoco.apps.survey.models import Answer, Question, Session
from recoco.apps.survey.serializers import (
    AnswerSerializer,
    QuestionSerializer,
    SessionSerializer,
)
from recoco.rest_api.permissions import IsStaffForSite


def projects_not_deleted_by_default(request):
    queryset = Project.all_on_site.for_user(request.user)
    if request_show_deleted_projects(request):
        queryset = queryset.filter(deleted=None)
    return queryset


class SessionFilterSet(filters_drf.FilterSet):
    project_id = ModelChoiceFilter(queryset=projects_not_deleted_by_default)

    class Meta:
        model = Session
        fields = ["project_id"]


class SessionView(ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = SessionFilterSet
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        project_ids = projects_not_deleted_by_default(self.request).values_list(
            "id", flat=True
        )
        return Session.objects.filter(project__in=project_ids)


class SessionAnswersView(ListAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        project_ids = projects_not_deleted_by_default(self.request).values_list(
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
