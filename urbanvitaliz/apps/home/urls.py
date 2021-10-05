# encoding: utf-8

"""
Urls for projects application

authors: raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created: 2021-05-26 15:54:25 CEST
"""


from django.urls import path

from . import views

urlpatterns = [
    path(r"", views.HomePageView.as_view(), name="home"),
    path(
        r"staff/dashboard", views.StaffDashboardView.as_view(), name="staff-dashboard"
    ),
    path(r"contact/", views.contact, name="home-contact"),
]

# eof
