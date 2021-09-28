import django.dispatch
from actstream import action
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

survey_started = django.dispatch.Signal()


@receiver(survey_started)
def log_survey_started(sender, survey, project, request, **kwargs):
    action.send(
        request.user,
        verb="a démarré le questionnaire",
        action_object=survey,
        target=project,
    )
