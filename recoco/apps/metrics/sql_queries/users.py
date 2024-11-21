from django.contrib.auth.models import User
from django.db.models import F, QuerySet

# from django.contrib.postgres.aggregates import ArrayAgg
# from django.contrib.sites.models import Site
# from django.db.models import TextField, Value, When, BooleanField, Case,
# from recoco.utils import make_group_name_for_site
from ..utils import hash_field


def get_queryset() -> QuerySet:
    # site = Site.objects.get(pk=site_id)

    # advisor_group_name = make_group_name_for_site("advisor", site)
    # staff_group_name = make_group_name_for_site("staff", site)

    return (
        User.objects.order_by("date_joined")
        .annotate(
            hash=hash_field("id", salt="user"),
            site_domain=F("profile__sites__domain"),
        )
        # .annotate(
        #     is_advisor=Case(
        #         When(groups__name=advisor_group_name, then=True),
        #         default=False,
        #         output_field=BooleanField(),
        #     ),
        #     advising_departments=ArrayAgg("profile__departments__code", distinct=True),
        # )
        # .annotate(
        #     is_site_staff=Case(
        #         When(groups__name=staff_group_name, then=True),
        #         default=False,
        #         output_field=BooleanField(),
        #     )
        # )
        # .annotate(
        #     advisor_scope=Case(
        #         When(
        #             is_advisor=True,
        #             profile__departments__isnull=True,
        #             then=Value("NATIO"),
        #         ),
        #         When(
        #             is_advisor=True,
        #             profile__departments__isnull=False,
        #             then=Value("REGIO"),
        #         ),
        #         default=None,
        #         output_field=TextField(),
        #     )
        # )
        .values(
            "hash",
            "site_domain",
            "date_joined",
            "last_login",
            # "is_advisor",
            # "advising_departments",
            # "advisor_scope",
            # "is_site_staff",
        )
        .order_by("hash")
        .distinct()
    )
