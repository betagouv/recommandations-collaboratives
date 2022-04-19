# encoding: utf-8

"""
Urls for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-04-19 14:54:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(
        r"invites/<uuid:invite_id>",
        views.invite_details,
        name="invites-invite-details",
    ),
    path(
        r"invites/<uuid:invite_id>/accept",
        views.invite_accept,
        name="invites-invite-accept",
    ),
]
