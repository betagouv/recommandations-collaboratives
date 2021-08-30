# encoding: utf-8

"""
Urls for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:54:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(r"onboarding/", views.onboarding, name="projects-onboarding"),
    # my projects for local authorities
    path(r"ma-collectivite/", views.local_authority, name="projects-local-authority"),
    # projects for switchtenders
    path(r"projects/", views.project_list, name="projects-project-list"),
    path("projects/feed/", views.LatestProjectsFeed(), name="projects-feed"),
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
        r"project/<int:project_id>/task/",
        views.create_task,
        name="projects-create-task",
    ),
    path(
        r"task/<int:task_id>/update/",
        views.update_task,
        name="projects-update-task",
    ),
    path(
        r"task/<int:task_id>/delete/",
        views.delete_task,
        name="projects-delete-task",
    ),
    path(
        r"project/<int:project_id>/note/",
        views.create_note,
        name="projects-create-note",
    ),
    path(
        r"note/<int:note_id>/delete/",
        views.delete_note,
        name="projects-delete-note",
    ),
    path(
        r"note/<int:note_id>/",
        views.update_note,
        name="projects-update-note",
    ),
    path(
        r"project/<int:project_id>/push/",
        views.push_resource,
        name="projects-push-resource",
    ),
    path(
        r"project/<int:resource_id>/resource/action/",
        views.create_resource_action,
        name="projects-create-resource-action",
    ),
    path(
        r"project/<int:project_id>/access/",
        views.access_update,
        name="projects-access-update",
    ),
    path(
        r"project/<int:project_id>/access/<str:email>/delete",
        views.access_delete,
        name="projects-access-delete",
    ),
]

# eof
