"""
Annotators add annotations in a database efficient way to Notification
before they are proceeded by Formatters. That way, the information needed to
format final messages (emails, in app notifications) don't need any database deep
relation to be loaded.
"""

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Q
from django.db.models.functions import JSONObject
from django.utils.functional import classproperty
from notifications.models import Notification

from recoco import verbs
from recoco.apps.conversations.models import ContactNode, DocumentNode


class JSONNotificationAnnotator:
    @classmethod
    def _build_json_object(self, data):
        """Given a standard python dict structure, create a JSON object using
        the db backend"""
        structure = {}
        for key, value in data.items():
            if type(value) is dict:
                structure.update({key: self._build_json_object(value)})
            else:
                structure.update({key: value})

        return JSONObject(**structure)

    @classmethod
    def make_annotations(cls):
        return cls._build_json_object(cls.annotations)

    @classproperty
    def annotations(cls):
        raise NotImplementedError

    prefetches = []
    selections = []


class MessageNotificationAnnotator(JSONNotificationAnnotator):
    verb = verbs.Conversation.POST_MESSAGE

    prefetches = ["action_messages", "action_messages__nodes"]

    @classproperty
    def annotations(cls):
        document_node_ct = ContentType.objects.get_for_model(DocumentNode)
        contact_node_ct = ContentType.objects.get_for_model(ContactNode)
        return {
            "documents": {
                "count": Count(
                    "action_messages__nodes",
                    filter=Q(
                        action_messages__nodes__polymorphic_ctype_id=document_node_ct
                    ),
                )
            },
            "contacts": {
                "count": Count(
                    "action_messages__nodes",
                    filter=Q(
                        action_messages__nodes__polymorphic_ctype_id=contact_node_ct
                    ),
                )
            },
        }


class NotificationAnnotator:
    """
    Annotates Notification objects with custom annotations
    Sample data:
    notification.annotations{
        "attachement_count": 2,
        "files": [{"name": "truc.pdf"}]
    }
    XXX Current limitation: a verb can be only matched by a single Annotator
    """

    annotator_classes = [MessageNotificationAnnotator]

    def __init__(self):
        self.annotators = [Annotator() for Annotator in self.annotator_classes]

    def annotated(self, notifications):
        notifications = notifications.annotate(annotations=JSONObject())
        notif_annotated = Notification.objects.none()

        for annotator in self.annotators:
            notif_annotated |= notif_annotated.union(
                notifications.filter(verb=annotator.verb)
                .select_related(*annotator.selections)
                .prefetch_related(*annotator.prefetches)
                .annotate(annotations=annotator.make_annotations())
            )

        return notif_annotated | notifications
