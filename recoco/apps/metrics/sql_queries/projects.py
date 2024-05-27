from django.db.models import Count, F, Q, QuerySet

from recoco.apps.projects.models import Project

from ..utils import hash_field


def get_queryset(site_id: int) -> QuerySet:
    return (
        Project.objects.exclude(exclude_stats=True)
        .prefetch_related("tasks", "switchtenders")
        .exclude(status="DRAFT")
        .order_by("created_on")
        .filter(sites__pk=site_id)
        .annotate(hash=hash_field("id", salt="project"))
        .annotate(
            recommandation_count=Count(
                "tasks", filter=Q(tasks__site__pk=site_id, tasks__public=True)
            ),
            advisor_count=Count("switchtenders_on_site", distinct=True),
            member_count=Count("projectmember", distinct=True),
        )
        .annotate(
            public_message_count=Count(
                "notes",
                filter=Q(notes__public=True),
                distinct=True,
            ),
            public_message_from_members_count=Count(
                "notes",
                filter=Q(notes__public=True, notes__created_by__in=F("members")),
                distinct=True,
            ),
            public_message_from_advisors_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__created_by__in=F("switchtenders_on_site__switchtender"),
                ),
                distinct=True,
            ),
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(notes__public=False),
                distinct=True,
            )
        )
        .annotate(
            crm_annotations_tags=StringAgg("crm_annotations__tags__name", delimiter=","),
            commune_insee=F("commune__insee"),
        )
        .values(
            "hash",
            "status",
            "created_on",
            "inactive_since",
            "commune_insee",
            "recommandation_count",
            "advisor_count",
            "member_count",
            "public_message_count",
            "public_message_from_members_count",  # FIXME: wrong
            "public_message_from_advisors_count",  # FIXME: wrong
            "private_message_count",
            "crm_annotations_tags",  # FIXME: wrong
        )
    )
