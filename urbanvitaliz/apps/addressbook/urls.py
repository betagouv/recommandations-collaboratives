# encoding: utf-8

"""
Urls for addressbook application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-16 16:22:25 CEST
"""


from django.urls import path

from . import views


urlpatterns = [
    path(
        r"addressbook/organizations/",
        views.organization_list,
        name="addressbook-organization-list",
    ),
    path(
        r"addressbook/organizations/create",
        views.organization_create,
        name="addressbook-organization-create",
    ),
    path(
        r"addressbook/organization/<int:organization_id>/",
        views.organization_details,
        name="addressbook-organization-details",
    ),
    path(
        r"addressbook/organization/<int:organization_id>/update/",
        views.organization_update,
        name="addressbook-organization-update",
    ),
    path(
        r"addressbook/organization/<int:organization_id>/create",
        views.contact_create,
        name="addressbook-organization-contact-create",
    ),
    path(
        r"addressbook/contact/<int:contact_id>/update/",
        views.contact_update,
        name="addressbook-organization-contact-update",
    ),
]
