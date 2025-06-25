# encoding: utf-8

"""
Urls for projects application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2025-06-25 15:54:25 CEST
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        r"",
        views.compare_resource,
        name="ml-summary",
    ),
]
