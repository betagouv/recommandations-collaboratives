# encoding: utf-8

"""
UrbanVitaliz URL configuration

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 11:29:25 CEST
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from django.urls import path, include

import debug_toolbar
from magicauth.urls import urlpatterns as magicauth_urls

from urbanvitaliz.apps.home.urls import urlpatterns as home_urls
from urbanvitaliz.apps.projects.urls import urlpatterns as projects_urls
from urbanvitaliz.apps.resources.urls import urlpatterns as resources_urls


urlpatterns = [
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("markdownx/", include("markdownx.urls")),
    path("nimda/", admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


urlpatterns.extend(magicauth_urls)
urlpatterns.extend(home_urls)
urlpatterns.extend(projects_urls)
urlpatterns.extend(resources_urls)

# eof
