from django.db.models import QuerySet


from recoco.apps.resources.models import Resource

from ..utils import hash_field, display_value


def get_queryset(site_id: int) -> QuerySet:
    return (
        Resource.objects.filter(sites__pk=site_id)
        .order_by("created_on")
        .annotate(hash=hash_field("id", salt="resource"))
        .annotate(status_name=display_value(Resource.STATUS_CHOICES, "status"))
        .annotate(created_by_hash=hash_field("created_by", salt="user"))
        .values(
            "hash",
            "status_name",
            "created_on",
            "updated_on",
            "created_by_hash",
        )
    )
