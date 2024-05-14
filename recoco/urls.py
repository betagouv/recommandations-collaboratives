# encoding: utf-8

"""
Recoco URL configuration

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
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls

from recoco.apps.addressbook import rest as addressbook_rest
from recoco.apps.addressbook.urls import urlpatterns as addressbook_urls
from recoco.apps.crm.urls import urlpatterns as crm_urls
from recoco.apps.geomatics import rest as geomatics_rest
from recoco.apps.home.urls import urlpatterns as home_urls
from recoco.apps.invites.urls import urlpatterns as invites_urls
from recoco.apps.onboarding.urls import urlpatterns as onboarding_urls
from recoco.apps.projects.urls import urlpatterns as projects_urls
from recoco.apps.projects.views import rest as projects_rest
from recoco.apps.resources import views as resources_views
from recoco.apps.resources.urls import urlpatterns as resources_urls
from recoco.apps.survey.urls import urlpatterns as survey_urls
from recoco.apps.tasks.urls import urlpatterns as tasks_urls
from recoco.apps.tasks.views import rest as tasks_rest
from recoco.apps.training import rest as training_rest

# Rest
router = routers.DefaultRouter()

router.register(
    r"projects/(?P<project_id>[^/.]+)/tasks/(?P<task_id>[^/.]+)/followups",
    tasks_rest.TaskFollowupViewSet,
    basename="project-tasks-followups",
)

router.register(
    r"projects/(?P<project_id>[^/.]+)/tasks",
    tasks_rest.TaskViewSet,
    basename="project-tasks",
)

router.register(
    r"projects/(?P<project_id>[^/.]+)/tasks/(?P<task_id>[^/.]+)/notifications",
    tasks_rest.TaskNotificationViewSet,
    basename="project-tasks-notifications",
)

router.register(r"resources", resources_views.ResourceViewSet, basename="resources")
router.register(
    r"departments", geomatics_rest.DepartmentViewSet, basename="departments"
)
router.register(r"regions", geomatics_rest.RegionViewSet, basename="regions")
router.register(r"communes", geomatics_rest.CommuneViewSet, basename="communes")
router.register(
    r"organizations", addressbook_rest.OrganizationViewSet, basename="organizations"
)
router.register(r"topics", projects_rest.TopicViewSet, basename="topics")
router.register(
    r"challenges/definitions",
    training_rest.ChallengeDefinitionViewSet,
    basename="challenge-definitions",
)

urlpatterns = [
    path("api/", include(router.urls)),
    path(
        "api/projects/<int:pk>/",
        projects_rest.ProjectDetail.as_view(),
        name="projects-detail",
    ),
    path(
        "api/projects/",
        projects_rest.ProjectList.as_view(),
        name="projects-list",
    ),
    path(
        "api/userprojectstatus/<int:pk>/",
        projects_rest.UserProjectStatusDetail.as_view(),
        name="userprojectstatus-detail",
    ),
    path(
        "api/userprojectstatus/",
        projects_rest.UserProjectStatusList.as_view(),
        name="userprojectstatus-list",
    ),
    path(
        "api/challenges/<str:slug>/",
        training_rest.ChallengeView.as_view(),
        name="challenges-challenge",
    ),
    path("accounts/", include("allauth.urls")),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("markdownx/", include("markdownx.urls")),
    path("notifications/", include(notifications.urls, namespace="notifications")),
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

    urlpatterns += [path(r"__debug__/", include(debug_toolbar.urls))]
#    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]


# eof
