# encoding: utf-8

"""
Urls for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 11:54:25 CEST
"""

from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path(
        r"onboarding",
        RedirectView.as_view(pattern_name="onboarding-project", query_string=True),
        name="onboarding",
    ),
    path(  # step 1
        r"onboarding/project",
        views.onboarding_project,
        name="onboarding-project",
    ),
    path(  # step 2
        r"onboarding/signup",
        views.onboarding_signup,
        name="onboarding-signup",
    ),
    path(  # step 3 through login for existing users
        r"onboarding/signin",
        views.OnboardingLogin.as_view(),
        name="onboarding-signin",
    ),
    # step 3 for email confirmation is included in login stage
    path(  # step 4 and final
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
]

# eof
