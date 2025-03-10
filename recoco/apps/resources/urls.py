# encoding: utf-8

"""
Urls for resources application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-06-16 11:05:44 CEST
"""

from django.urls import path

from . import views

urlpatterns = [
    path(
        r"ressource/",
        views.resource_search,
        name="resources-resource-search",
    ),
    path(
        r"ressource/feed/",
        views.LatestResourcesFeed(),
        name="resources-feed",
    ),
    path(
        r"ressource/create/",
        views.resource_create,
        name="resources-resource-create",
    ),
    path(
        r"ressource/<int:resource_id>/",
        views.ResourceDetailView.as_view(),
        name="resources-resource-detail",
    ),
    path(
        r"ressource/<int:resource_id>/delete",
        views.ResourceDeleteView.as_view(),
        name="resources-resource-delete",
    ),
    path(
        r"ressource/<int:resource_id>/embed",
        views.EmbededResourceDetailView.as_view(),
        name="resources-resource-detail-embeded",
    ),
    path(
        r"ressource/<int:resource_id>/update/",
        views.resource_update,
        name="resources-resource-update",
    ),
    path(
        "ressource/<path:pk>/revision/",
        views.ResourceHistoryCompareView.as_view(),
        name="resources-resource-history",
    ),
    path(
        "ressource/<path:pk>/revision/<int:rev_pk>",
        views.ResourceHistoryRestoreView.as_view(),
        name="resources-resource-history-restore",
    ),
    path(
        r"ressource/<int:resource_id>/bookmark/create/",
        views.create_bookmark,
        name="resources-bookmark-create",
    ),
    path(
        r"ressource/<int:resource_id>/bookmark/delete/",
        views.delete_bookmark,
        name="resources-bookmark-delete",
    ),
]

# eof
