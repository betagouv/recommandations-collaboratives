from django.urls import path

from rest_framework import routers

from recoco.apps.addressbook import rest as addressbook_rest
from recoco.apps.geomatics import rest as geomatics_rest
from recoco.apps.projects.views import rest as projects_rest
from recoco.apps.tasks.views import rest as tasks_rest
from recoco.apps.training import rest as training_rest
from recoco.apps.resources import rest as resources_rest
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
router.register(
    r"resources",
    resources_rest.ResourceViewSet,
    basename="resources",
)
router.register(
    r"departments",
    geomatics_rest.DepartmentViewSet,
    basename="departments",
)
router.register(
    r"regions",
    geomatics_rest.RegionViewSet,
    basename="regions",
)
router.register(
    r"communes",
    geomatics_rest.CommuneViewSet,
    basename="communes",
)
router.register(
    r"organizations",
    addressbook_rest.OrganizationViewSet,
    basename="organizations",
)
router.register(
    r"topics",
    projects_rest.TopicViewSet,
    basename="topics",
)
router.register(
    r"challenges/definitions",
    training_rest.ChallengeDefinitionViewSet,
    basename="challenge-definitions",
)

api_urls = [
    path(
        "projects/<int:pk>/",
        projects_rest.ProjectDetail.as_view(),
        name="projects-detail",
    ),
    path(
        "projects/",
        projects_rest.ProjectList.as_view(),
        name="projects-list",
    ),
    path(
        "userprojectstatus/<int:pk>/",
        projects_rest.UserProjectStatusDetail.as_view(),
        name="userprojectstatus-detail",
    ),
    path(
        "userprojectstatus/",
        projects_rest.UserProjectStatusList.as_view(),
        name="userprojectstatus-list",
    ),
    path(
        "challenges/<str:slug>/",
        training_rest.ChallengeView.as_view(),
        name="challenges-challenge",
    ),
]

auth_urls = [
    path(
        "token/",
        TokenObtainPairView.as_view(),
        name="token",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(),
        name="token-refresh",
    ),
]

urlpatterns = router.urls + api_urls + auth_urls
