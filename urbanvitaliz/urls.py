# encoding: utf-8

"""
UrbanVitaliz URL configuration

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 11:29:25 CEST
"""

import notifications.urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from magicauth.urls import urlpatterns as magicauth_urls
from rest_framework import routers

from urbanvitaliz.apps.addressbook.urls import urlpatterns as addressbook_urls
from urbanvitaliz.apps.geomatics import rest as geomatics_rest
from urbanvitaliz.apps.home.urls import urlpatterns as home_urls
from urbanvitaliz.apps.projects.urls import urlpatterns as projects_urls
from urbanvitaliz.apps.projects.views import rest as projects_rest
from urbanvitaliz.apps.resources import views as resources_views
from urbanvitaliz.apps.resources.urls import urlpatterns as resources_urls
from urbanvitaliz.apps.survey.urls import urlpatterns as survey_urls

# Rest
router = routers.DefaultRouter()
router.register(r"projects", projects_rest.ProjectViewSet, basename="projects")
router.register(r"resources", resources_views.ResourceViewSet, basename="resources")
router.register(
    r"departments", geomatics_rest.DepartmentViewSet, basename="departments"
)


urlpatterns = [
    path("api/", include(router.urls)),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("markdownx/", include("markdownx.urls")),
    path("notifications/", include(notifications.urls, namespace="notifications")),
    path("hijack/", include("hijack.urls")),
    path("nimda/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns.extend(magicauth_urls)
urlpatterns.extend(home_urls)
urlpatterns.extend(projects_urls)
urlpatterns.extend(resources_urls)
urlpatterns.extend(addressbook_urls)
urlpatterns.extend(survey_urls)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [path(r"__debug__/", include(debug_toolbar.urls))]

# eof
