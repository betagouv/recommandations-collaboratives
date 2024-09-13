import collections

import pytest
from django.contrib.sites.shortcuts import get_current_site
from django.utils import timezone
from model_bakery import baker

from recoco.apps.projects import models as projects_models
from recoco.apps.tasks import models as tasks_models

from .. import views

########################################################################
# topics tag cloud
########################################################################


@pytest.mark.django_db
def test_compute_topics_tag_cloud(request):
    site = get_current_site(request)
    topic0 = baker.make(projects_models.Topic, site=site, name="topic0")
    topic1 = baker.make(projects_models.Topic, site=site, name="topic1")
    topic2 = baker.make(projects_models.Topic, site=site, name="topic2")
    project = baker.make(projects_models.Project, sites=[site], name="theproject")
    project.topics.set([topic0, topic2])
    task = baker.make(
        tasks_models.Task, project=project, site=site, topic=topic0, intent="thetask"
    )

    # topics on deleted project should not be counted
    deleted_project = baker.make(
        projects_models.Project,
        sites=[site],
        name="thedeletedproject",
        deleted=timezone.now(),
    )
    deleted_project.topics.set([topic1])

    # topics on deleted task should not be counted
    baker.make(
        tasks_models.Task,
        project=project,
        site=site,
        topic=topic1,
        intent="thedeletedtask",
        deleted=timezone.now(),
    )

    topics = views.compute_topics_occurences(site)
    assert topics == collections.OrderedDict(
        [
            (
                "topic0",
                (2, [("theproject", project.pk)], [("thetask", task.pk, project.pk)]),
            ),
            ("topic2", (1, [("theproject", project.pk)], [])),
        ]
    )


# eof
