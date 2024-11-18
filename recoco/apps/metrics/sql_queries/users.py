from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.sites.models import Site
from django.db.models import BooleanField, Case, QuerySet, TextField, Value, When

from recoco.utils import make_group_name_for_site

from ..utils import hash_field


def get_queryset(site_id: int | None) -> QuerySet:
    queryset = User.objects
    if site_id:
        queryset = queryset.filter(profile__sites__pk=site_id)

    queryset = User.objects.order_by("date_joined").annotate(
        hash=hash_field("id", salt="user")
    )

    values = [
        "hash",
        "date_joined",
        "last_login",
    ]

    if site_id:
        site = Site.objects.get(pk=site_id)
        advisor_group_name = make_group_name_for_site("advisor", site)
        staff_group_name = make_group_name_for_site("staff", site)

        queryset = (
            queryset.annotate(
                is_advisor=Case(
                    When(groups__name=advisor_group_name, then=True),
                    default=False,
                    output_field=BooleanField(),
                ),
                advising_departments=ArrayAgg(
                    "profile__departments__code", distinct=True
                ),
            )
            .annotate(
                is_site_staff=Case(
                    When(groups__name=staff_group_name, then=True),
                    default=False,
                    output_field=BooleanField(),
                )
            )
            .annotate(
                advisor_scope=Case(
                    When(
                        is_advisor=True,
                        profile__departments__isnull=True,
                        then=Value("NATIO"),
                    ),
                    When(
                        is_advisor=True,
                        profile__departments__isnull=False,
                        then=Value("REGIO"),
                    ),
                    default=None,
                    output_field=TextField(),
                )
            )
        )

        values += [
            "is_advisor",
            "is_site_staff",
            "advising_departments",
            "advisor_scope",
        ]

    return queryset.values(*values).order_by("hash").distinct()
