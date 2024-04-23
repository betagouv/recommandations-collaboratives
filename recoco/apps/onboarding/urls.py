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
        views.OnboardingView.as_view(),
        name="projects-onboarding",
    ),
    path(
        r"onboarding/signup",
        views.onboarding_signup,
        name="projects-onboarding-signup",
    ),
    path(
        r"onboarding/project",
        views.onboarding_project,
        name="projects-onboarding-project",
    ),
    path(
        r"onboarding/summary/<int:project_id>",
        views.onboarding_summary,
        name="projects-onboarding-summary",
    ),
    path(
        r"onboarding/prefill/signup",
        views.create_user_for_project_prefilled,
        name="projects-project-prefill-signup",
    ),
    path(
        r"onboarding/prefill/project",
        views.create_project_for_project_prefilled,
        name="projects-project-prefill-project",
    ),
    path(
        r"onboarding/<int:project_id>/commune/",
        views.select_commune,
        name="projects-onboarding-select-commune",
    ),
]

# eof
