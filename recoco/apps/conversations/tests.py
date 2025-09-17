import pytest
from django.contrib.auth import models as auth_models
from django.contrib.sites.shortcuts import get_current_site
from model_bakery import baker

from recoco.apps.tasks import signals as tasks_signals
from recoco.apps.tasks.models import Task

from .models import Message
from .utils import post_public_message_with_recommendation


#####--- Utils ---#####
@pytest.mark.django_db
def test_post_message_with_recommendation(project_ready, request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    task = baker.make(
        Task, public=True, project=project_ready, site=current_site, created_by=user
    )

    assert Message.objects.count() == 0

    post_public_message_with_recommendation(project_ready, task)

    assert Message.objects.count() == 1


#####--- Signals ---#####
@pytest.mark.django_db
def test_message_is_posted_upon_reco_creation(project_ready, request):
    current_site = get_current_site(request)
    user = baker.make(auth_models.User)

    assert Message.objects.count() == 0

    tasks_signals.action_created.send(
        sender=test_message_is_posted_upon_reco_creation,
        task=Task.objects.create(
            public=True,
            project=project_ready,
            site=current_site,
            created_by=user,
        ),
        project=project_ready,
        user=user,
    )

    assert Message.objects.count() == 1
