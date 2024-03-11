# encoding: utf-8

"""
Urls for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 11:54:25 CEST
"""


from django.urls import path

from . import views

# FIXME rename the following urls removing projects prefix -> OK

urlpatterns = [
    path(
        r"onboarding/",
        views.onboarding,
        name="projects-onboarding",
    ),
    path(
        r"onboarding/signin",
        views.onboarding_step1_signin,
        name="projects-onboarding-signin",
    ),
    path(
        r"onboarding/signup",
        views.onboarding_step1_signup,
        name="projects-onboarding-signup",
    ),
    path(
        r"onboarding/project",
        views.onboarding_step2_project,
        name="projects-onboarding-project",
    ),
    path(
        r"onboarding/summary/<int:project_id>",
        views.onboarding_summary,
        name="projects-onboarding-summary",
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
