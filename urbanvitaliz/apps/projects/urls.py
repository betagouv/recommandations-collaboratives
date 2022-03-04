# encoding: utf-8

"""
Urls for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:54:25 CEST
"""


from django.urls import path

from . import views
from .views import feeds, notes, sharing, tasks

urlpatterns = [
    path(r"onboarding/", views.onboarding, name="projects-onboarding"),
    path(
        r"onboarding/<int:project_id>/commune/",
        views.select_commune,
        name="projects-onboarding-select-commune",
    ),
    path(
        r"login_redirect/",
        views.redirect_user_to_project,
        name="projects-redirect-user-to-project",
    ),
    # projects for switchtenders
    path(r"projects/", views.project_list, name="projects-project-list"),
    path("projects/feed/", feeds.LatestProjectsFeed(), name="projects-feed"),
    path(
        r"project/<int:project_id>/",
        views.project_detail,
        name="projects-project-detail",
    ),
    path(
        r"project/<int:project_id>/update/",
        views.project_update,
        name="projects-project-update",
    ),
    path(
        r"project/<int:project_id>/switchtender/join",
        views.project_switchtender_join,
        name="projects-project-switchtender-join",
    ),
    path(
        r"project/<int:project_id>/suggestions/",
        tasks.presuggest_task,
        name="projects-project-tasks-suggest",
    ),
    path(
        r"project/partage/<str:project_ro_key>/",
        views.project_detail_from_sharing_link,
        name="projects-project-sharing-link",
    ),
    path(
        r"project/<int:project_id>/accept/",
        views.project_accept,
        name="projects-project-accept",
    ),
    path(
        r"project/<int:project_id>/delete/",
        views.project_delete,
        name="projects-project-delete",
    ),
    path(
        r"task/<int:task_id>/update/",
        tasks.update_task,
        name="projects-update-task",
    ),
    path(
        r"task/<int:task_id>/visit/",
        tasks.visit_task,
        name="projects-visit-task",
    ),
    path(
        r"task/<int:task_id>/toggle-done/",
        tasks.toggle_done_task,
        name="projects-toggle-done-task",
    ),
    path(
        r"task/<int:task_id>/refuse/",
        tasks.refuse_task,
        name="projects-refuse-task",
    ),
    path(
        r"task/<int:task_id>/already/",
        tasks.already_done_task,
        name="projects-already-done-task",
    ),
    path(
        r"task/<int:task_id>/delete/",
        tasks.delete_task,
        name="projects-delete-task",
    ),
    path(
        r"task/<int:task_id>/remind/",
        tasks.remind_task,
        name="projects-remind-task",
    ),
    path(
        r"task/<int:task_id>/remind-delete/",
        tasks.remind_task_delete,
        name="projects-remind-task-delete",
    ),
    path(
        r"task/<int:task_id>/followup/",
        tasks.followup_task,
        name="projects-followup-task",
    ),
    path(
        r"task/rsvp/<uuid:rsvp_id>/<int:status>/",
        tasks.rsvp_followup_task,
        name="projects-rsvp-followup-task",
    ),
    path(
        r"project/<int:project_id>/conversation/",
        notes.create_public_note,
        name="projects-conversation-create-message",
    ),
    path(
        r"project/<int:project_id>/note/",
        notes.create_note,
        name="projects-create-note",
    ),
    path(
        r"note/<int:note_id>/delete/",
        notes.delete_note,
        name="projects-delete-note",
    ),
    path(
        r"note/<int:note_id>/",
        notes.update_note,
        name="projects-update-note",
    ),
    path(
        r"project/<int:resource_id>/resource/action/",
        tasks.create_resource_action_for_current_project,
        name="projects-create-resource-action",
    ),
    path(
        r"project/<int:project_id>/action/",
        tasks.create_action,
        name="projects-project-create-action",
    ),
    path(
        r"project/<int:project_id>/access/",
        sharing.access_update,
        name="projects-access-update",
    ),
    path(
        r"project/<int:project_id>/access/<str:email>/delete",
        sharing.access_delete,
        name="projects-access-delete",
    ),
    # Recommendations
    path(
        r"projects/task-recommendation",
        tasks.task_recommendation_list,
        name="projects-task-recommendation-list",
    ),
    path(
        r"projects/task-recommendation/create",
        tasks.task_recommendation_create,
        name="projects-task-recommendation-create",
    ),
    path(
        r"projects/task-recommendation/<int:recommendation_id>/update",
        tasks.task_recommendation_update,
        name="projects-task-recommendation-update",
    ),
]

# eof
