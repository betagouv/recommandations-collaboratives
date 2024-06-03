from django.db.models import Count, F, Q, QuerySet, Subquery, OuterRef, Func
from django.contrib.postgres.aggregates import StringAgg

from recoco.apps.projects.models import Project, ProjectSwitchtender
from recoco.apps.tasks.models import Task

from ..utils import hash_field


def get_queryset(site_id: int) -> QuerySet:
    return (
        Project.objects.exclude(exclude_stats=True)
        .prefetch_related("tasks", "switchtenders")
        .exclude(status="DRAFT")
        .order_by("-created_on")
        .filter(sites__pk=site_id)
        .annotate(hash=hash_field("id", salt="project"))
        .annotate(
            recommandation_count=Subquery(
                Task.objects.filter(
                    project_id=OuterRef("pk"), site_id=site_id, public=True
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            ),
            advisor_count=Subquery(
                ProjectSwitchtender.objects.filter(
                    project_id=OuterRef("pk"), site_id=site_id
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            ),
            member_count=Count("members", distinct=True),
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
            crm_annotations_tags=StringAgg(
                "crm_annotations__tags__name", delimiter=","
            ),
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
            "crm_annotations_tags",
        )
    )
