from actstream.models import Action
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, QuerySet, Value
from django.db.models.functions import Cast

from recoco import verbs
from recoco.apps.tasks.models import TaskFollowup

from ..utils import hash_field


def _get_actions(site_id: int | None) -> QuerySet:
    site_filter = {"site__pk": site_id} if site_id else {}

    UserCT = ContentType.objects.get_for_model(User)

    return (
        Action.objects.filter(**site_filter)
        .filter(public=True, actor_content_type=UserCT)
        .filter(
            verb__in=[
                verbs.Project.INVITATION,
                verbs.Project.BECAME_OBSERVER,
                verbs.Project.BECAME_ADVISOR,
                verbs.Survey.STARTED,
                verbs.Survey.UPDATED,
                verbs.Conversation.PUBLIC_MESSAGE,
                verbs.Conversation.PRIVATE_MESSAGE,
                verbs.Document.ADDED,
                verbs.Recommendation.CREATED,
                verbs.Recommendation.COMMENTED,
            ]
        )
        .annotate(
            user_hash=hash_field("actor_object_id", salt="user"),
            event_name=F("verb"),
            when=Cast("timestamp", output_field=models.DateField()),
        )
        .values(
            "user_hash",
            "event_name",
            "when",
        )
    )


def _get_task_followup(site_id: int | None) -> QuerySet:
    task_site_filter = {"task__site__pk": site_id} if site_id else {}

    return (
        TaskFollowup.objects.filter(**task_site_filter)
        .exclude(status=None)
        .annotate(
            user_hash=hash_field("who", salt="user"),
            event_name=Value(
                "a mis à jour l'état de la recommandation",
                output_field=models.TextField(),
            ),
            when=Cast("timestamp", output_field=models.DateField()),
        )
        .values(
            "user_hash",
            "event_name",
            "when",
        )
    )


def get_queryset(site_id: int | None) -> QuerySet:
    activity = _get_actions(site_id)
    reco_status_updated = _get_task_followup(site_id)
    return activity.union(reco_status_updated)
