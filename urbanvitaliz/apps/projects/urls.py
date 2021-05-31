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
    # projects for switchtenders
    path(r"projects/", views.project_list, name="projects-project-list"),
    path(
        r"project/<int:project_id>/",
        views.project_detail,
        name="projects-project-detail",
    ),
    path(
        r"project/<int:project_id>/task/",
        views.create_task,
        name="projects-create-task",
    ),
    path(
        r"project/<int:project_id>/note/",
        views.create_note,
        name="projects-create-note",
    ),
]

# eof
