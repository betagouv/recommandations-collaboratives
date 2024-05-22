import pytest
from django.contrib.sites.models import Site
from django_webhook.models import WebhookTopic
from model_bakery import baker

from recoco.apps.projects.models import Project

from ..models import WebhookSite
from ..signals import WebhookSignalListener


@pytest.fixture
def webhook():
    webhook_topic, _ = WebhookTopic.objects.get_or_create(name="topic")

    webhook = baker.make("django_webhook.Webhook", active=True)
    webhook.topics.add(webhook_topic)

    WebhookSite.objects.create(site=Site.objects.first(), webhook=webhook)
    yield webhook


@pytest.fixture
def project():
    project = baker.make("projects.Project")
    project.sites.add(Site.objects.first())
    yield project


def build_listener():
    return WebhookSignalListener(
        signal=None, signal_name="post_save", model_cls=Project
    )


@pytest.mark.django_db
def test_find_webhooks_ok(webhook, project):
    assert build_listener().find_webhooks("topic", project) == [
        (webhook.id, webhook.uuid)
    ]


@pytest.mark.django_db
def test_find_webhooks_not_active(webhook, project):
    webhook.active = False
    webhook.save()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_topics(webhook, project):
    webhook.topics.clear()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_sites(webhook, project):
    project.sites.clear()
    assert build_listener().find_webhooks("topic", project) == []


@pytest.mark.django_db
def test_find_webhooks_no_project():
    task = baker.make("tasks.Task")
    assert build_listener().find_webhooks("topic", task) == []


@pytest.mark.skip(reason="TODO")
def test_model_dict(project):
    assert (
        build_listener().model_dict(
            Project(
                id=1,
                name="name",
                status="status",
            )
        )
        == {}
    )
