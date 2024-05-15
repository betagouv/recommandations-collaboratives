from django.db.models import QuerySet
from django.db.models import F, Count, Value
from recoco.apps.projects.models import Project
from django.db.models.functions import Coalesce

# Number of projects in activity per day for a given site


def get_queryset(site_id: int) -> QuerySet:
    return (
        Project.objects.filter(sites__pk=site_id)
        .annotate(day=F("last_members_activity_at__date"))
        .values("day")
        .order_by("-day")
        .annotate(count=Coalesce(Count("id", distinct=True), Value(0)))
    )
