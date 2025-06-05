from django.contrib.contenttypes.models import ContentType
from django.db.models import (
    BooleanField,
    Case,
    CharField,
    Exists,
    F,
    OuterRef,
    QuerySet,
    Value,
    When,
)
from django.db.models.functions import Concat, Lower, Replace

from recoco.apps.hitcount.models import Hit
from recoco.apps.projects.models import ProjectMember

from ..utils import hash_field


def get_queryset() -> QuerySet:
    contact_ct = ContentType.objects.get(app_label="addressbook", model="contact")
    resource_ct = ContentType.objects.get(app_label="resources", model="resource")
    user_ct = ContentType.objects.get(app_label="auth", model="user")
    project_ct = ContentType.objects.get(app_label="projects", model="project")

    return (
        Hit.objects.annotate(
            hit_type=Case(
                When(
                    hitcount__content_object_ct=contact_ct,
                    hitcount__context_object_ct=resource_ct,
                    then=Value("contact_resource"),
                ),
                When(
                    hitcount__content_object_ct=user_ct,
                    hitcount__context_object_ct=project_ct,
                    then=Value("ref_contact"),
                ),
                default=None,
                output_field=CharField(),
            ),
        )
        .exclude(hit_type__isnull=True)
        .annotate(
            hash=hash_field("id", salt="hit"),
            user_hash=hash_field("user", salt="user"),
        )
        .annotate(
            site_domain=F("hitcount__site__domain"),
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
        )
        .annotate(
            staff_group_name=Concat(
                "site_slug",
                Value("_staff"),
            ),
            user_is_staff=Case(
                When(user__groups__name=F("staff_group_name"), then=True),
                default=False,
                output_field=BooleanField(),
            ),
            advisor_group_name=Concat(
                "site_slug",
                Value("_advisor"),
            ),
            user_is_advisor=Case(
                When(user__groups__name=F("advisor_group_name"), then=True),
                default=False,
                output_field=BooleanField(),
            ),
            user_is_project_member=Exists(
                ProjectMember.objects.filter(
                    member=OuterRef("user"),
                    project__project_sites__site=OuterRef("hitcount__site"),
                )
            ),
        )
        .values(
            "hash",
            "site_domain",
            "hit_type",
            "created",
            "user_hash",
            "user_is_staff",
            "user_is_advisor",
            "user_is_project_member",
        )
        .order_by("hash")
        .distinct()
    )
