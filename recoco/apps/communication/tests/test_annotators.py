import pytest
from django.contrib.auth import models as auth_models
from model_bakery import baker
from notifications.models import Notification

from recoco import verbs
from recoco.apps.projects import models as projects_models

from ..annotators import NotificationAnnotator


@pytest.mark.django_db
def test_message_annotator():
    user = baker.make(
        auth_models.User, username="Bob", first_name="Bobi", last_name="Joe"
    )
    note = baker.make(projects_models.Note)

    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=note,
        public=True,
    )

    na = NotificationAnnotator()
    notifications = na.annotated(Notification.objects.all())

    for notification in notifications:
        assert "documents" in notification.annotations
        assert "contacts" in notification.annotations


@pytest.mark.skip
@pytest.mark.django_db
def test_annotator_honors_verb_restriction():
    user = baker.make(
        auth_models.User, username="Bob", first_name="Bobi", last_name="Joe"
    )
    note = baker.make(projects_models.Note)

    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=note,
        public=True,
    )
    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.PRIVATE_MESSAGE,
        action_object=note,
        public=True,
    )

    na = NotificationAnnotator()
    notifications = na.annotated(Notification.objects.all())

    for notification in notifications.exclude(verb=verbs.Conversation.POST_MESSAGE):
        assert "documents" not in notification.annotations


@pytest.mark.django_db
def test_annotator_keeps_unhandled_notifications():
    user = baker.make(
        auth_models.User, username="Bob", first_name="Bobi", last_name="Joe"
    )
    note = baker.make(projects_models.Note)

    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.POST_MESSAGE,
        action_object=note,
        public=True,
    )
    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.PRIVATE_MESSAGE,
        action_object=note,
        public=True,
    )

    na = NotificationAnnotator()
    notifications = na.annotated(Notification.objects.all())

    assert Notification.objects.count() == notifications.count()


@pytest.mark.django_db
def test_annotator_does_not_modify_unhandled_notifications():
    user = baker.make(
        auth_models.User, username="Bob", first_name="Bobi", last_name="Joe"
    )
    note = baker.make(projects_models.Note)

    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.PRIVATE_MESSAGE,
        action_object=note,
        public=True,
    )
    baker.make(
        Notification,
        actor=user,
        verb=verbs.Conversation.PRIVATE_MESSAGE,
        action_object=note,
        public=True,
    )

    na = NotificationAnnotator()
    notifications = na.annotated(Notification.objects.all())

    assert set(Notification.objects.all()) == set(notifications.all())
