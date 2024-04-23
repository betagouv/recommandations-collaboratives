# encoding: utf-8

"""
Urls for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 11:54:25 CEST
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        r"onboarding/",
        views.OnboardingView.as_view(),
        name="onboarding",
    ),
    path(
        r"onboarding/signup",
        views.onboarding_signup,
        name="onboarding-signup",
    ),
    path(
        r"onboarding/project",
        views.onboarding_project,
        name="onboarding-project",
    ),
    path(
        r"onboarding/summary/<int:project_id>",
        views.onboarding_summary,
        name="onboarding-summary",
    ),
    path(
        r"onboarding/prefill/setuser",
        views.prefill_project_set_user,
        name="onboarding-prefill-set-user",
    ),
    path(
        r"onboarding/prefill/project",
        views.prefill_project_submit,
        name="onboarding-prefill",
    ),
    path(
        r"onboarding/<int:project_id>/commune/",
        views.select_commune,
        name="onboarding-select-commune",
    ),
]

# eof
