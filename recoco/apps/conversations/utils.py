#!/usr/bin/env python

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from . import models, signals
from .models import ContactNode, DocumentNode, RecommendationNode


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

        node_count = 1

        if recommendation.contact:
            node_count += 1
            ContactNode.objects.create(
                message=msg, position=node_count, contact=recommendation.contact
            )

        for document in recommendation.document.all():
            node_count += 1
            DocumentNode.objects.create(
                message=msg, position=node_count, document=document
            )

        signals.message_posted.send(
            sender=post_public_message_with_recommendation, message=msg
        )

    return msg


def gather_annotations_for_message_notification(message):
    document_node_ct = ContentType.objects.get_for_model(DocumentNode)
    contact_node_ct = ContentType.objects.get_for_model(ContactNode)
    reco_node_ct = ContentType.objects.get_for_model(RecommendationNode)

    return {
        "documents": {
            "count": message.nodes.filter(polymorphic_ctype_id=document_node_ct).count()
        },
        "contacts": {
            "count": message.nodes.filter(polymorphic_ctype_id=contact_node_ct).count()
        },
        "recommendations": {
            "count": message.nodes.filter(polymorphic_ctype_id=reco_node_ct).count()
        },
    }
