from actstream.models import Action
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F, QuerySet, Value
from django.db.models.functions import Cast

from recoco import verbs
from recoco.apps.tasks.models import TaskFollowup

from ..utils import hash_field


def get_queryset() -> QuerySet:
    UserCT = ContentType.objects.get_for_model(User)
    activity = (
        Action.objects.filter(public=True, actor_content_type=UserCT)
        .filter(
            verb__in=[
                verbs.Project.INVITATION,
                verbs.Project.BECAME_OBSERVER,
                verbs.Project.BECAME_ADVISOR,
                verbs.Survey.STARTED,
                verbs.Survey.UPDATED,
                verbs.Conversation.POST_MESSAGE,
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
            site_domain=F("site__domain"),
        )
        .values(
            "user_hash",
            "site_domain",
            "event_name",
            "when",
        )
    )

    reco_status_updated = (
        TaskFollowup.objects.exclude(status=None)
        .annotate(
            user_hash=hash_field("who", salt="user"),
            event_name=Value(
                "a mis à jour l'état de la recommandation",
                output_field=models.TextField(),
            ),
            when=Cast("timestamp", output_field=models.DateField()),
            site_domain=F("task__site__domain"),
        )
        .values(
            "user_hash",
            "site_domain",
            "event_name",
            "when",
        )
    )

    return activity.union(reco_status_updated)
