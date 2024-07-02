import pytest
from django.contrib.sites.models import Site
from django_webhook.models import WebhookTopic
from freezegun import freeze_time
from model_bakery import baker

from recoco.apps.geomatics.models import Commune
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
def commune():
    return baker.make(
        Commune,
        name="Bayonne",
        insee="64102",
        postal="64100",
        latitude=43.4933,
        longitude=-1.4753,
        department__code="64",
        department__name="Pyrénées-Atlantiques",
    )


@pytest.fixture
def project(commune):
    with freeze_time("2024-05-22"):
        project = baker.make(
            "projects.Project",
            status="READY",
            name="My project",
            org_name="My organization",
            commune=commune,
            description="My description",
        )
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


@pytest.mark.django_db
def test_model_dict(project):
    print(build_listener().model_dict(project))
    assert build_listener().model_dict(project) == {
        "id": project.id,
        "name": "My project",
        "description": "My description",
        "status": "READY",
        "inactive_since": None,
        "created_on": "2024-05-22T02:00:00+02:00",
        "updated_on": "2024-05-22T02:00:00+02:00",
        "org_name": "My organization",
        "switchtenders": [],
        "commune": {
            "name": "Bayonne",
            "insee": "64102",
            "postal": "64100",
            "department": {"name": "Pyrénées-Atlantiques", "code": "64"},
            "latitude": 43.4933,
            "longitude": -1.4753,
        },
        "recommendation_count": 0,
        "public_message_count": 0,
        "private_message_count": 0,
    }
