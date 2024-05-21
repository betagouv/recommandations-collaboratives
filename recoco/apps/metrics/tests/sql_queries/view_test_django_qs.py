from recoco.apps.projects.models import Project
from django.db.models import Count, QuerySet


def get_queryset(site_id: int) -> QuerySet:
    return (
        Project.objects.filter(sites__id=site_id)
        .values("id")
        .annotate(task_count=Count("tasks"))
    )
