from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.apps.survey import models as survey_models
from urbanvitaliz.utils import check_if_advisor, get_site_config_or_503

from .utils import can_administrate_project, get_active_project


def is_switchtender_processor(request):
    return {
        "is_switchtender": check_if_advisor(request.user),
        "is_administrating_project": can_administrate_project(
            project=None, user=request.user
        ),
    }


def active_project_processor(request):
    active_project = get_active_project(request)
    context = {
        "active_project": active_project,
    }

    if request.user.is_authenticated:
        # Retrieve notification count
        project_ct = ContentType.objects.get_for_model(projects_models.Project)
        unread_notifications_for_projects = request.user.notifications.unread().filter(
            public=True,
            target_content_type=project_ct.pk,
        )

        context.update(
            {
                "unread_notifications_count": unread_notifications_for_projects.count(),
            }
        )

    if active_project:
        try:
            site_config = get_site_config_or_503(request.site)
            session, _ = survey_models.Session.objects.get_or_create(
                project=active_project, survey=site_config.project_survey
            )
        except (survey_models.Survey.DoesNotExist, ImproperlyConfigured):
            session = None

        # Retrieve notification count
        project_notifications = request.user.notifications.filter(
            target_content_type=project_ct.pk,
            target_object_id=active_project.pk,
        )

        # Task notifications
        task_ct = ContentType.objects.get_for_model(projects_models.Task)
        task_followup_ct = ContentType.objects.get_for_model(
            projects_models.TaskFollowup
        )
        action_notifications_count = (
            project_notifications.filter(
                Q(action_object_content_type=task_ct)
                | Q(action_object_content_type=task_followup_ct)
            )
            .unread()
            .count()
        )

        note_ct = ContentType.objects.get_for_model(projects_models.Note)
        # Conversations notifications
        conversation_notifications_count = (
            project_notifications.filter(
                action_object_content_type=note_ct, action_notes__public=True
            )
            .unread()
            .count()
        )

        # Internal conversations notifications
        private_conversation_notifications_count = (
            project_notifications.filter(
                action_object_content_type=note_ct, action_notes__public=False
            )
            .unread()
            .count()
        )

        document_ct = ContentType.objects.get_for_model(projects_models.Document)
        # Document notifications
        document_notifications_count = (
            project_notifications.filter(
                action_object_content_type=document_ct,
            )
            .unread()
            .count()
        )

        context.update(
            {
                "active_project_can_administrate": can_administrate_project(
                    active_project, request.user
                ),
                "active_project_survey_session": session,
                "active_project_action_notifications_count": action_notifications_count,
                "active_project_conversation_notifications_count": conversation_notifications_count,  # noqa
                "active_project_document_notifications_count": document_notifications_count,  # noqa
                "active_project_private_conversation_notifications_count": private_conversation_notifications_count,  # noqa
            }
        )

    return context


# eof
