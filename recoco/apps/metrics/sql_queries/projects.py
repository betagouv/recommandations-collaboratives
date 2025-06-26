from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, F, Func, OuterRef, Q, QuerySet, Subquery

from recoco.apps.projects.models import Project, ProjectSwitchtender
from recoco.apps.tasks.models import Task

from ..utils import hash_field


def get_queryset() -> QuerySet:
    return (
        Project.objects.exclude(exclude_stats=True)
        .prefetch_related("tasks", "switchtenders")
        .exclude(project_sites__status="DRAFT")
        .order_by("-created_on")
        .annotate(
            hash=hash_field("id", salt="project"),
            site_domain=F("sites__domain"),
            site_id=F("sites__id"),
        )
        # .exclude(project_sites__site__pk=F("site_id"))
        .annotate(
            recommandation_count=Subquery(
                Task.objects.filter(
                    project_id=OuterRef("pk"),
                    site_id=OuterRef("site_id"),
                    public=True,
                )
                .order_by()
                .annotate(count=Func(F("id"), function="Count"))
                .values("count")
            ),
            advisor_count=Subquery(
                ProjectSwitchtender.objects.filter(
                    project_id=OuterRef("pk"),
                    site_id=OuterRef("site_id"),
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
                filter=Q(
                    notes__public=True,
                    notes__site_id=F("site_id"),
                ),
                distinct=True,
            ),
            public_message_from_members_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__site_id=F("site_id"),
                    notes__created_by__in=F("members"),
                ),
                distinct=True,
            ),
            public_message_from_advisors_count=Count(
                "notes",
                filter=Q(
                    notes__public=True,
                    notes__site_id=F("site_id"),
                    notes__created_by__in=F("switchtender_sites__switchtender"),
                ),
                distinct=True,
            ),
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(
                    notes__public=False,
                    notes__site_id=F("site_id"),
                ),
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
            commune_latitude=F("commune__latitude"),
            commune_longitude=F("commune__longitude"),
        )
        .annotate(
            status=F("project_sites__status"),
            filter=Q(project_sites__site__pk=F("site_id")),
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
            "site_domain",
            "status",
            "created_on",
            "inactive_since",
            "commune_insee",
            "commune_latitude",
            "commune_longitude",
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
