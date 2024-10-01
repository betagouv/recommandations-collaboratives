from typing import Any

import django.dispatch
from actstream import action
from django.db.models.signals import post_save
from django.dispatch import receiver

from recoco import verbs

from ..projects.tasks import collect_survey_answers_in_project
from .models import Answer

survey_session_started = django.dispatch.Signal()

survey_session_updated = django.dispatch.Signal()

# FIXME not covered by a test


@receiver(survey_session_started)
def log_survey_started(sender, survey, project, request, **kwargs):
    if project.project_sites.current().status == "DRAFT" or project.muted:
        return

    if not request.user.is_staff:
        action.send(
            request.user,
            verb=verbs.Survey.STARTED,
            action_object=survey,
            target=project,
        )


@receiver(post_save, sender=Answer)
def trigger_collect_survey_answers_in_project(
    sender: Any, instance: Answer, created: bool, **kwargs
):
    collect_survey_answers_in_project.delay(instance.session.project_id)
