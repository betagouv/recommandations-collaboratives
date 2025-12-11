import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_webhook.models import WebhookTopic
from freezegun import freeze_time
from model_bakery import baker
from taggit.models import TaggedItem

from recoco.apps.addressbook.models import Organization
from recoco.apps.geomatics.models import Commune
from recoco.apps.projects.models import Project, ProjectSwitchtender

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
        department__region__code="75",
        department__region__name="Nouvelle-Aquitaine",
    )


@pytest.fixture
def organization():
    return baker.make(Organization, name="Jedi corp")


@pytest.fixture
def project(commune, organization, make_project, current_site):
    with freeze_time("2024-05-22"):
        project = make_project(
            name="My project",
            org_name="My organization",
            commune=commune,
            location="rue des basques",
            location_x=635731.78681425,
            location_y=3644425.1077159,
            description="My description",
            advisors_note="Note interne",
        )
        project.tags.add("my_tag")  # taggit doesn't support initialization

        user = User.objects.get_or_create(
            email="anakin@jedi.com",
            username="anakin",
        )[0]

        user.profile.organization_position = "Padawan"
        user.profile.organization = organization
        user.profile.save()

        baker.make(
            ProjectSwitchtender, site=current_site, switchtender=user, project=project
        )

        yield project


@pytest.fixture
def serialized_project(project, organization):
    return {
        "id": project.id,
        "name": "My project",
        "description": "My description",
        "inactive_since": None,
        "created_on": "2024-05-22T02:00:00+02:00",
        "updated_on": "2024-05-22T02:00:00+02:00",
        "org_name": "My organization",
        "switchtenders": [
            {
                "email": "anakin@jedi.com",
                "first_name": "",
                "is_active": True,
                "last_name": "",
                "profile": {
                    "organization": {
                        "_link": f"/api/addressbook/organizations/{organization.id}/",
                        "id": organization.id,
                        "name": "Jedi corp",
                        "group": {"id": organization.group.id, "name": "Jedi corp"},
                    },
                    "organization_position": "Padawan",
                },
                "username": "anakin",
            }
        ],
        "location": "rue des basques",
        "latitude": 3644425.1077159,
        "longitude": 635731.78681425,
        "commune": {
            "name": "Bayonne",
            "insee": "64102",
            "postal": "64100",
            "department": {
                "name": "Pyrénées-Atlantiques",
                "code": "64",
                "region": {
                    "name": "Nouvelle-Aquitaine",
                    "code": "75",
                },
            },
            "latitude": 43.4933,
            "longitude": -1.4753,
        },
        "recommendation_count": 0,
        "public_message_count": 0,
        "private_message_count": 0,
        "project_sites": [
            {
                "id": project.project_sites.current().pk,
                "site": 1,
                "is_origin": True,
                "status": "READY",
            }
        ],
        "tags": [
            "my_tag",
        ],
        "is_diagnostic_done": False,
        "status": "READY",
        "advisors_note": None,
        "exclude_stats": False,
        "muted": False,
    }


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
def test_model_dict_project(project, serialized_project):
    dict_project = build_listener().model_dict(project)
    assert dict_project == serialized_project


@pytest.mark.django_db
def test_model_dict_taggeditem(project, serialized_project):
    project_ct = ContentType.objects.get_for_model(project)
    tagged_item = TaggedItem.objects.get(
        content_type=project_ct, object_id=project.pk, tag__name="my_tag"
    )
    assert build_listener().model_dict(tagged_item) == serialized_project


@pytest.mark.django_db
def test_model_dict_answer(project):
    with freeze_time("2024-05-22"):
        answer = baker.make(
            "survey.Answer",
            question__text="question",
            session__project=project,
        )

    assert build_listener().model_dict(answer) == {
        "id": answer.id,
        "created_on": "2024-05-22T02:00:00+02:00",
        "updated_on": "2024-05-22T02:00:00+02:00",
        "question": {
            "id": answer.question_id,
            "text": "question",
            "text_short": "",
            "slug": "question",
            "is_multiple": False,
            "choices": [],
        },
        "session": answer.session_id,
        "project": project.id,
        "choices": [],
        "values": [],
        "comment": "",
        "signals": "",
        "updated_by": None,
        "attachment": None,
    }


def test_model_dict_other():
    assert build_listener().model_dict(instance="dummy") == {}
