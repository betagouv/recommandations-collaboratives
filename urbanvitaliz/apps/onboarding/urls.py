# encoding: utf-8

"""
Urls for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 11:54:25 CEST
"""


from django.urls import path

from . import views

# FIXME rename the following urls removing projects prefix

urlpatterns = [
    path(
        r"onboarding/",
        views.onboarding,
        name="projects-onboarding",
    ),
    path(
        r"onboarding/prefill/",
        views.create_project_prefilled,
        name="projects-project-prefill",
    ),
    path(
        r"onboarding/<int:project_id>/commune/",
        views.select_commune,
        name="projects-onboarding-select-commune",
    ),
]

# eof
