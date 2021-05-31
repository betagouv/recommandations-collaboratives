# encoding: utf-8

"""
UrbanVitaliz URL configuration

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 11:29:25 CEST
"""

from django.contrib import admin
from django.urls import path

from magicauth import views as magicauth_views
from magicauth.urls import urlpatterns as magicauth_urls

from urbanvitaliz.apps.projects.urls import urlpatterns as projects_urls


urlpatterns = [
    path("admin/", admin.site.urls),
]

urlpatterns.extend(magicauth_urls)
urlpatterns.extend(projects_urls)

# eof
