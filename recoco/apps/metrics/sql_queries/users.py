from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import BooleanField, Case, QuerySet, TextField, Value, When

from recoco.utils import make_group_name_for_site

from ..utils import hash_field


def get_queryset(site_id: int) -> QuerySet:
    site = Site.objects.get(pk=site_id)

    advisor_group_name = make_group_name_for_site("advisor", site)
    staff_group_name = make_group_name_for_site("staff", site)

    return (
        User.objects.filter(profile__sites__pk=site_id)
        .order_by("date_joined")
        .annotate(hash=hash_field("id", salt="user"))
        .annotate(
            is_advisor=Case(
                When(groups__name=advisor_group_name, then=True),
                default=False,
                output_field=BooleanField(),
            )
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
        .values(
            "hash",
            "date_joined",
            "is_advisor",
            "advisor_scope",
            "is_site_staff",
            "last_login",
        )
        .order_by("hash")
        .distinct("hash")
    )
