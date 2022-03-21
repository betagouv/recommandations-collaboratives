from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import check_if_switchtender

from .utils import (can_administrate_project, can_manage_project,
                    get_active_project)


def is_switchtender_processor(request):
    return {"is_switchtender": check_if_switchtender(request.user)}


def active_project_processor(request):
    active_project = get_active_project(request)
    context = {
        "active_project": active_project,
    }

    if active_project:
        try:
            survey = survey_models.Survey.objects.get(pk=1)  # XXX Hardcoded survey ID
            session, created = survey_models.Session.objects.get_or_create(
                project=active_project, survey=survey
            )
        except survey_models.Survey.DoesNotExist:
            session = None

        context.update(
            {
                "active_project_can_manage": can_manage_project(
                    active_project, request.user
                ),
                "active_project_can_administrate": can_administrate_project(
                    active_project, request.user
                ),
                "active_project_survey_session": session,
            }
        )

    return context
