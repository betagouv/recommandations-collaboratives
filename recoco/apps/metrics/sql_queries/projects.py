from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, F, Func, OuterRef, Q, QuerySet, Subquery

from recoco.apps.projects.models import Project, ProjectSwitchtender
from recoco.apps.tasks.models import Task

from ..utils import hash_field


def get_queryset(site_id: int | None) -> QuerySet:
    # site filters and subquery site filters
    if site_id:
        site_filter = {"sites__pk": site_id}
        task_site_filter = {"site_id": site_id}
        switchtender_site_filter = {"site_id": site_id}
        note_site_filter = {"notes__site_id": site_id}
    else:
        site_filter = {}
        task_site_filter = {}
        switchtender_site_filter = {}
        note_site_filter = {}

    # exclusion filters
    exclude_filter = {"project_sites__status": "DRAFT"}
    if site_id:
        exclude_filter.update({"project_sites__site__pk": site_id})

    return (
        Project.objects.exclude(exclude_stats=True)
        .prefetch_related("tasks", "switchtenders")
        .exclude(**exclude_filter)
        .order_by("-created_on")
        .filter(**site_filter)
        .annotate(
            hash=hash_field("id", salt="project"),
            recommandation_count=Subquery(
                Task.objects.filter(
                    project_id=OuterRef("pk"), public=True, **task_site_filter
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            ),
            advisor_count=Subquery(
                ProjectSwitchtender.objects.filter(
                    project_id=OuterRef("pk"), **switchtender_site_filter
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            ),
            member_count=Count("members", distinct=True),
            public_message_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    **note_site_filter,
                ),
                distinct=True,
            ),
            public_message_from_members_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__created_by__in=F("members"),
                    **note_site_filter,
                ),
                distinct=True,
            ),
            public_message_from_advisors_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__created_by__in=F("switchtender_sites__switchtender"),
                    **note_site_filter,
                ),
                distinct=True,
            ),
            private_message_count=Count(
                "notes",
                filter=Q(
                    notes__public=False,
                    **note_site_filter,
                ),
                distinct=True,
            ),
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
