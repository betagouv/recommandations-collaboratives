from django.contrib.auth.models import User
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import BooleanField, Case, F, QuerySet, TextField, Value, When
from django.db.models.functions import Concat, Lower, Replace

from ..utils import hash_field


def get_queryset() -> QuerySet:
    return (
        User.objects.order_by("date_joined")
        .annotate(
            hash=hash_field("id", salt="user"),
            site_domain=F("profile__sites__domain"),
            site_slug=Lower(
                Replace(
                    Replace(
                        "site_domain",
                        Value("-"),
                        Value("_"),
                    ),
                    Value("."),
                    Value("_"),
                )
            ),
            advisor_group_name=Concat("site_slug", Value("_advisor")),
            staff_group_name=Concat("site_slug", Value("_staff")),
        )
        .annotate(
            is_advisor=Case(
                When(groups__name=F("advisor_group_name"), then=True),
                default=False,
                output_field=BooleanField(),
            ),
            advising_departments=ArrayAgg("profile__departments__code", distinct=True),
        )
        .annotate(
            is_site_staff=Case(
                When(groups__name=F("staff_group_name"), then=True),
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
        .values(
            "hash",
            "site_domain",
            "date_joined",
            "last_login",
            "is_advisor",
            "advising_departments",
            "advisor_scope",
            "is_site_staff",
        )
        .order_by("hash")
        .distinct()
    )
