from django.db.models import F, QuerySet

from recoco.apps.resources.models import Resource

from ..utils import display_value, hash_field


def get_queryset() -> QuerySet:
    return (
        Resource.objects.order_by("created_on")
        .annotate(
            hash=hash_field("id", salt="resource"),
            site_domain=F("sites__domain"),
        )
        .annotate(status_name=display_value(Resource.STATUS_CHOICES, "status"))
        .annotate(created_by_hash=hash_field("created_by", salt="user"))
        .values(
            "hash",
            "site_domain",
            "status_name",
            "created_on",
            "updated_on",
            "created_by_hash",
        )
    )
