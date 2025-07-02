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
        r"compare/resource/propose",
        views.propose_resource_comparison,
        name="ml-resource-comparison-propose",
    ),
    path(
        r"compare/resource/<int:comparison_id>",
        views.show_resource_comparison,
        name="ml-resource-comparison-show",
    ),
    path(
        r"compare/<int:comparison_id>/update",
        views.update_comparison,
        name="ml-comparison-update",
    ),
]
