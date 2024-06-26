from django.urls import path
from notifications import views as notifications_views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from recoco.apps.addressbook import rest as addressbook_rest
from recoco.apps.geomatics import rest as geomatics_rest
from recoco.apps.home import rest as home_rest
from recoco.apps.projects.views import rest as projects_rest
from recoco.apps.resources import rest as resources_rest
from recoco.apps.tasks.views import rest as tasks_rest
from recoco.apps.training import rest as training_rest
from recoco.apps.survey.views import rest as survey_rest

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
    path(
        "notifications/mark-one-as-read/<int:pk>/",
        home_rest.UserNotificationsMarkOneAsRead.as_view(),
        name="notifications-mark-one-as-read",
    ),
    path(
        "notifications/mark-all-as-read",
        home_rest.UserNotificationsMarkAllAsRead.as_view(),
        name="notifications-mark-all-as-read",
    ),
    path(
        "notifications/unread_list",
        notifications_views.live_unread_notification_list,
        name="notifications-unread-list",
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

survey_urls = [
    path(
        "survey/sessions/",
        survey_rest.SessionView.as_view(),
        name="api-survey-sessions",
    ),
    path(
        "survey/sessions/<int:session_id>/answers/",
        survey_rest.SessionAnswersView.as_view(),
        name="api-survey-session-answers",
    ),
]

urlpatterns = router.urls + api_urls + auth_urls + survey_urls
