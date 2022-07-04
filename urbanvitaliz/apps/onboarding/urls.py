# encoding: utf-8

"""
Urls for onboarding application

author  : guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created : 2022-06-06 11:54:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(r"onboarding/", views.onboarding, name="projects-onboarding"),
]

# eof
