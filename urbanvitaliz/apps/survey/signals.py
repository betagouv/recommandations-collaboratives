import django.dispatch
from actstream import action
from django.dispatch import receiver

survey_session_started = django.dispatch.Signal()

survey_session_updated = django.dispatch.Signal()


@receiver(survey_session_started)
def log_survey_started(sender, survey, project, request, **kwargs):
    if not request.user.is_staff:
        action.send(
            request.user,
            verb="a démarré le questionnaire",
            action_object=survey,
            target=project,
        )
