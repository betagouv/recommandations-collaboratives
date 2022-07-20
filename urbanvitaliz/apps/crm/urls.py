# encoding: utf-8

"""
Urls for crm application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2022-07-19 17:27:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(
        r"crm/org/<int:organization_id>/",
        views.organization_details,
        name="crm-organization-details",
    ),
]
