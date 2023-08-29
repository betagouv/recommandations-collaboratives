# encoding: utf-8

"""
Test for models and functions avaiable in models

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-29 13:59:10 CEST
"""

import pytest
from django.conf import settings
from django.contrib.sites import models as sites
from model_bakery import baker

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
    task = baker.make(models.Task, project=project, site=site, topic=task_topic)

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

    task = baker.make(models.Task, project=project, site=site, topic=topic)

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


# eof
