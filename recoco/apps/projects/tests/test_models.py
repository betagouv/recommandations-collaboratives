# encoding: utf-8

"""
Test for models and functions avaiable in models

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-29 13:59:10 CEST
"""

import pytest
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites import models as sites
from django.utils import timezone
from model_bakery import baker
from notifications.models import Notification

from recoco.apps.projects.models import Note
from recoco.apps.tasks import models as task_models
from recoco.apps.tasks.models import Task, TaskFollowup

from .. import models


@pytest.mark.django_db
def test_project_returns_its_topics_and_its_tasks_ones():
    site = baker.make(sites.Site)
    # a project with two topics and a task w/ its own topic
    project_topics = baker.make(models.Topic, site=site, _quantity=2)
    project = baker.make(models.Project)
    project.sites.add(site)
    project.topics.set(project_topics)

    task_topic = baker.make(models.Topic, site=site)
    baker.make(task_models.Task, project=project, site=site, topic=task_topic)

    # all topics of project should include its topics and its tasks' ones
    with settings.SITE_ID.override(site.pk):
        all_topics = list(project.all_topics)

    assert task_topic in all_topics
    assert all(t in all_topics for t in project_topics)


@pytest.mark.django_db
def test_project_all_topics_are_not_duplicated():
    site = baker.make(sites.Site)
    # a project and its task with the same topic
    topic = baker.make(models.Topic, site=site)
    project = baker.make(models.Project)
    project.sites.add(site)
    project.topics.add(topic)

    baker.make(task_models.Task, project=project, site=site, topic=topic)

    # topic is not duplicated in all topics for project
    with settings.SITE_ID.override(site.pk):
        all_topics = list(project.all_topics)

    assert all_topics == [topic]


@pytest.mark.django_db
def test_project_all_topics_exclude_other_site_topics():
    site = baker.make(sites.Site)
    # a project and its task with the same topic
    topic = baker.make(models.Topic)
    project = baker.make(models.Project)
    project.sites.add(site)
    project.topics.add(topic)

    # topic is not duplicated in all topics for project
    with settings.SITE_ID.override(site.pk):
        all_topics = list(project.all_topics)

    assert all_topics == []


@pytest.mark.django_db
def test_project_all_topics_exclude_deleted_tasks():
    site = baker.make(sites.Site)
    topic = baker.make(models.Topic, site=site)
    project = baker.make(models.Project)
    project.sites.add(site)
    baker.make(
        task_models.Task,
        project=project,
        site=site,
        topic=topic,
        deleted=timezone.now(),
    )

    # topic is not duplicated in all topics for project
    with settings.SITE_ID.override(site.pk):
        all_topics = list(project.all_topics)

    assert all_topics == []


# ProjectSite QuerySet
@pytest.mark.django_db
def test_projectsite_queryset():
    site = baker.make(sites.Site)
    site2 = baker.make(sites.Site)
    project = baker.make(models.Project)
    project.project_sites.create(site=site, status="DRAFT")
    project.project_sites.create(site=site2, status="READY", is_origin=True)

    assert project.project_sites.count() == 2
    assert project.project_sites.moderated().count() == 1
    assert project.project_sites.to_moderate().count() == 1
    assert project.project_sites.origin().site == site2

    with settings.SITE_ID.override(site.id):
        assert project.project_sites.current().site == site


@pytest.mark.django_db
def test_project_queryset_unread_notifications():
    project = baker.make(models.Project)
    user = baker.make(settings.AUTH_USER_MODEL)
    public_note = baker.make(Note, project=project, public=True)
    private_note = baker.make(Note, project=project, public=False)

    project_ct = ContentType.objects.get_for_model(models.Project)
    task_ct = ContentType.objects.get_for_model(Task)
    task_followup_ct = ContentType.objects.get_for_model(TaskFollowup)
    note_ct = ContentType.objects.get_for_model(Note)

    baker.make(
        Notification,
        recipient=user,
        target_object_id=project.id,
        target_content_type=project_ct,
        unread=True,
        action_object_content_type=task_ct,
    )
    baker.make(
        Notification,
        recipient=user,
        target_object_id=project.id,
        target_content_type=project_ct,
        unread=True,
        action_object_content_type=task_followup_ct,
    )
    baker.make(
        Notification,
        recipient=user,
        target_object_id=project.id,
        target_content_type=project_ct,
        unread=True,
        action_object_content_type=note_ct,
        action_object_object_id=public_note.id,
    )
    baker.make(
        Notification,
        recipient=user,
        target_object_id=project.id,
        target_content_type=project_ct,
        unread=True,
        action_object_content_type=note_ct,
        action_object_object_id=private_note.id,
    )

    annotated_project = models.Project.objects.with_unread_notifications(
        user.id
    ).first()
    assert annotated_project.action_notifications_count == 2
    assert annotated_project.conversation_notifications_count == 1
    assert annotated_project.private_conversation_notifications_count == 1
    assert annotated_project.document_notifications_count == 0


# eof
