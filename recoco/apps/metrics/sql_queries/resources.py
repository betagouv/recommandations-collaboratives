from django.db.models import F, QuerySet

from recoco.apps.resources.models import Resource

from ..utils import display_value, hash_field


def get_queryset(site_id: int | None) -> QuerySet:
    site_filter = {"sites__pk": site_id} if site_id else {}

    return (
        Resource.objects.filter(**site_filter)
        .order_by("created_on")
        .annotate(
            hash=hash_field("id", salt="resource"),
            status_name=display_value(Resource.STATUS_CHOICES, "status"),
            created_by_hash=hash_field("created_by", salt="user"),
            sites_domain=F("sites__domain"),
        )
        .values(
            "hash",
            "status_name",
            "created_on",
            "updated_on",
            "created_by_hash",
            "sites_domain",
        )
    )
