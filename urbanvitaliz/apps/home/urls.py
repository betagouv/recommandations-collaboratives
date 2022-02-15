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
    path(r"login-redirect", views.LoginRedirectView.as_view(), name="login-redirect"),
    path(r"stats", views.StatisticsView.as_view(), name="statistics"),
    path(r"methodologie", views.MethodologyPageView.as_view(), name="methodology"),
    path(r"qui-sommes-nous", views.WhoWeArePageView.as_view(), name="whoweare"),
    path(r"nous-suivre", views.FollowUsPageView.as_view(), name="followus"),
    path(
        r"staff/dashboard",
        views.SwitchtenderDashboardView.as_view(),
        name="switchtender-dashboard",
    ),
    path(r"contact/", views.contact, name="home-contact"),
]

# eof
