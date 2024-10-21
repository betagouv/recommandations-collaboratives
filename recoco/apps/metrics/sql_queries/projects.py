from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, F, Func, OuterRef, Q, QuerySet, Subquery

from recoco.apps.projects.models import Project, ProjectSwitchtender
from recoco.apps.tasks.models import Task

from ..utils import hash_field


def get_queryset(site_id: int) -> QuerySet:
    return (
        Project.objects.exclude(exclude_stats=True)
        .prefetch_related("tasks", "switchtenders")
        .exclude(project_sites__status="DRAFT", project_sites__site__pk=site_id)
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
                filter=Q(notes__public=True, notes__site_id=site_id),
                distinct=True,
            ),
            public_message_from_members_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__site_id=site_id,
                    notes__created_by__in=F("members"),
                ),
                distinct=True,
            ),
            public_message_from_advisors_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__site_id=site_id,
                    notes__created_by__in=F("switchtender_sites__switchtender"),
                ),
                distinct=True,
            ),
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(notes__public=False, notes__site_id=site_id),
                distinct=True,
            )
        )
        .annotate(
            project_topics=ArrayAgg(
                "topics__name",
                distinct=True,
            ),
            crm_annotations_tags=ArrayAgg(
                "crm_annotations__tags__name",
                distinct=True,
            ),
            advised_by=ArrayAgg(
                hash_field("switchtenders__id", salt="user"),
                distinct=True,
            ),
            commune_insee=F("commune__insee"),
        )
        .annotate(
            status=F("project_sites__status"), filter=Q(project_sites__site__pk=site_id)
        )
        .annotate(
            site_origin=F("project_sites__site__domain"),
            filter=Q(project_sites__is_origin=True),
        )
        .annotate(
            all_sites=F("project_sites__site__domain"),
            filter=~Q(project_sites__status=["DRAFT", "REJECTED"]),
        )
        .values(
            "hash",
            "status",
            "created_on",
            "inactive_since",
            "commune_insee",
            "recommandation_count",
            "advisor_count",
            "advised_by",
            "member_count",
            "public_message_count",
            "public_message_from_members_count",  # FIXME: wrong
            "public_message_from_advisors_count",  # FIXME: wrong
            "private_message_count",
            "project_topics",
            "crm_annotations_tags",
            "site_origin",
            "all_sites",
        )
    )
