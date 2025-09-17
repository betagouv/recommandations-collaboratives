#!/usr/bin/env python

from django.db import transaction

from . import models
from .models import RecommendationNode


def make_public_message(project, sender):
    return models.Message(project=project, posted_by=sender)


def post_public_message_with_recommendation(recommendation, text=None):
    with transaction.atomic():
        msg = make_public_message(recommendation.project, recommendation.created_by)
        msg.save()

        RecommendationNode.objects.create(
            message=msg,
            position=1,
            text=text or recommendation.content,
            recommendation=recommendation,
        )

    return msg
