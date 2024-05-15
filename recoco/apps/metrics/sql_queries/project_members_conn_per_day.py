from django.db.models import QuerySet
from django.db.models import F, Count, Value
from recoco.apps.projects.models import ProjectMember
from django.db.models.functions import Coalesce

# Number of member connections per day for a given site


def get_queryset(site_id: int) -> QuerySet:
    return (
        ProjectMember.objects.filter(project__sites__pk=site_id)
        .annotate(day=F("member__last_login__date"))
        .values("day")
        .order_by("-day")
        .annotate(count=Coalesce(Count("id", distinct=True), Value(0)))
    )
