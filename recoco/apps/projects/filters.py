from datetime import timedelta

from actstream.models import Action
from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField, F, Func, OuterRef, Q, Subquery
from django.db.models.functions import Cast
from django.utils import timezone
from rest_framework.filters import BaseFilterBackend

from recoco.apps.projects.models import Project


class ProjectActivityFilter(BaseFilterBackend):
    """
    Filter on users activity using action streams and project annotation
    """

    def filter_queryset(self, request, queryset, view):
        last_activity_days = request.GET.get("last_activity", None)

        project_ct = ContentType.objects.get_for_model(Project)

        if last_activity_days:
            try:
                from_ts = timezone.now() - timedelta(days=int(last_activity_days))
            except ValueError:
                return queryset

            # Fetch activity from actstream
            queryset = (
                queryset.annotate(
                    recent_actions_count=Subquery(
                        Action.objects.filter(
                            target_content_type_id=project_ct.pk,
                            target_object_id=Cast(OuterRef("pk"), CharField()),
                            timestamp__gte=from_ts,
                        )
                        .order_by()
                        .annotate(count=Func(F("id"), function="Count"))
                        .values("count")
                    ),
                )
                .filter(
                    # We want both to cover members and advisors activities
                    Q(last_members_activity_at__gte=from_ts)
                    | Q(recent_actions_count__gt=0)
                )
                .distinct()
            )

        return queryset


class DepartmentsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        departments = request.GET.getlist("departments", None)
        if departments:
            queryset = queryset.filter(commune__department__code__in=departments)
        return queryset


class ProjectSiteStatusFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        project_site_status = request.GET.getlist("status", None)
        if project_site_status:
            queryset = queryset.filter(project_site_status__in=project_site_status)
        return queryset
