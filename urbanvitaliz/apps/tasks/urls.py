# encoding: utf-8

"""
Urls for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:54:25 CEST
"""


from django.urls import path

from .views import (
    tasks,
)

urlpatterns = [
    path(
        r"project/<int:resource_id>/resource/action/",
        tasks.create_resource_action_for_current_project,
        name="projects-create-resource-action",
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
    path(
        r"project/<int:project_id>/action/",
        tasks.create_task,
        name="projects-project-create-task",
    ),
    path(
        r"task/<int:task_id>/update/",
        tasks.update_task,
        name="projects-update-task",
    ),
    path(
        r"task/<int:task_id>/sort/<str:order>",
        tasks.sort_task,
        name="projects-sort-task",
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
        r"task/followup/<int:followup_id>/edit/",
        tasks.followup_task_update,
        name="projects-task-followup-update",
    ),
    path(
        r"task/rsvp/<uuid:rsvp_id>/<int:status>/",
        tasks.rsvp_followup_task,
        name="projects-rsvp-followup-task",
    ),
]

# eof
