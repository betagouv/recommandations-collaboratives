from django.db.models import QuerySet
from django.contrib.auth import get_user_model
from django.db.models import F, Count

# Number of switchtenders connections per day for a given site


def get_queryset(site_id: int) -> QuerySet:
    return (
        get_user_model()
        .objects.filter(
            projects_switchtended_on_site__site_id=site_id,
        )
        .annotate(last_login_day=F("last_login__date"))
        .values("last_login_day")
        .order_by("-last_login_day")
        .annotate(count=Count("id", distinct=True))
    )
