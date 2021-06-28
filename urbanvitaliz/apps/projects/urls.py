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
    path(r"macollectivite/", views.local_authority, name="projects-local-authority"),
    # projects for switchtenders
    path(r"projects/", views.project_list, name="projects-project-list"),
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
        r"project/<int:project_id>/task/",
        views.create_task,
        name="projects-create-task",
    ),
    path(
        r"task/<int:task_id>/",
        views.update_task,
        name="projects-update-task",
    ),
    path(
        r"project/<int:project_id>/note/",
        views.create_note,
        name="projects-create-note",
    ),
    path(
        r"note/<int:note_id>/",
        views.update_note,
        name="projects-update-note",
    ),
]

# eof
