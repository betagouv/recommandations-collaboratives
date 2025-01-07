# encoding: utf-8

"""
Recoco URL configuration

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 11:29:25 CEST
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from magicauth.urls import urlpatterns as magicauth_urls
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from recoco.apps.addressbook.urls import urlpatterns as addressbook_urls
from recoco.apps.crm.urls import urlpatterns as crm_urls
from recoco.apps.home.urls import urlpatterns as home_urls
from recoco.apps.invites.urls import urlpatterns as invites_urls
from recoco.apps.onboarding.urls import urlpatterns as onboarding_urls
from recoco.apps.projects.urls import urlpatterns as projects_urls
from recoco.apps.resources.urls import urlpatterns as resources_urls
from recoco.apps.survey.urls import urlpatterns as survey_urls
from recoco.apps.tasks.urls import urlpatterns as tasks_urls
from recoco.rest_api.urls import urlpatterns as rest_api_urls

urlpatterns = [
    path("api/", include(rest_api_urls)),
    path("accounts/", include("allauth.urls")),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("markdownx/", include("markdownx.urls")),
    path("hijack/", include("hijack.urls")),
    path("nimda/", admin.site.urls),
    path("cookies/", include("cookie_consent.urls")),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("p/", include(wagtail_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns.extend(magicauth_urls)
urlpatterns.extend(home_urls)
urlpatterns.extend(onboarding_urls)
urlpatterns.extend(projects_urls)
urlpatterns.extend(tasks_urls)
urlpatterns.extend(resources_urls)
urlpatterns.extend(addressbook_urls)
urlpatterns.extend(survey_urls)
urlpatterns.extend(invites_urls)
urlpatterns.extend(crm_urls)

if settings.DEBUG:
    import debug_toolbar
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path(r"__debug__/", include(debug_toolbar.urls)),
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/schema/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
        path(
            "api/schema/redoc/",
            SpectacularRedocView.as_view(url_name="schema"),
            name="redoc",
        ),
    ]
    #    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

# eof
