from django.db.models import Count, F, QuerySet

from recoco.apps.projects.models import Project


def get_queryset() -> QuerySet:
    return Project.objects.annotate(
        site_domain=F("sites__domain"),
        task_count=Count("tasks"),
    ).values(
        "id",
        "site_domain",
        "task_count",
    )
