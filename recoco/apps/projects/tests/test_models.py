# encoding: utf-8

"""
Test for models and functions avaiable in models

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-08-29 13:59:10 CEST
"""

import pytest
from django.conf import settings
from django.contrib.sites import models as sites
from django.utils import timezone
from model_bakery import baker

from recoco.apps.tasks import models as task_models

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


@pytest.mark.parametrize(
    "lookup_key, expected_value",
    [
        ("name", "my project"),
        ("dummy", None),
        ("dummy.dummy", None),
        ("survey_answers.thematiques.comment", "Friche"),
        ("survey_answers.thematiques.dummy_value", None),
        (
            "survey_answers.thematiques.answers",
            "Patrimoine, Transition énergétique, Autre",
        ),
        ("survey_answers.dummy_value", None),
        ("commune.name", "Bayonne"),
        ("commune.dummy", None),
    ],
)
def test_project_get_from_lookup_key(lookup_key, expected_value):
    project = baker.prepare(
        models.Project,
        name="my project",
        commune__name="Bayonne",
        survey_answers={
            "calendrier": {"answers": [], "comment": "A définir"},
            "thematiques": {
                "answers": "Patrimoine, Transition énergétique, Autre",
                "comment": "Friche",
            },
        },
    )
    assert project.get_from_lookup_key(lookup_key) == expected_value


# eof
