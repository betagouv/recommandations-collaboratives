import importlib

from django.urls import path
from notifications import views as notifications_views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from recoco.apps.addressbook import rest as addressbook_rest
from recoco.apps.conversations import rest as conversations_rest
from recoco.apps.geomatics import rest as geomatics_rest
from recoco.apps.home import rest as home_rest
from recoco.apps.projects.views import rest as projects_rest
from recoco.apps.resources import rest as resources_rest
from recoco.apps.survey.views import rest as survey_rest
from recoco.apps.tasks.views import acra_proxy as tasks_acra_proxy
from recoco.apps.tasks.views import rest as tasks_rest
from recoco.apps.training import rest as training_rest

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
    r"resource-addons",
    resources_rest.ResourceAddonViewSet,
    basename="resource-addons",
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
    r"topics",
    projects_rest.TopicViewSet,
    basename="topics",
)
router.register(
    r"projects/(?P<project_id>[^/.]+)/documents",
    projects_rest.DocumentViewSet,
    basename="projects-documents",
)
router.register(
    r"challenges/definitions",
    training_rest.ChallengeDefinitionViewSet,
    basename="challenge-definitions",
)
router.register(
    r"projects/projectsites",
    projects_rest.ProjectSiteViewSet,
    basename="projects-projectsites",
)
router.register(
    r"projects/(?P<project_id>[^/.]+)/conversations/messages",
    conversations_rest.MessageViewSet,
    basename="projects-conversations-messages",
)
router.register(
    r"projects/(?P<project_id>[^/.]+)/conversations/activities",
    conversations_rest.ActivityViewSet,
    basename="projects-conversations-activities",
)
router.register(
    r"projects/(?P<project_id>[^/.]+)/conversations/participants",
    conversations_rest.ParticipantViewSet,
    basename="projects-conversations-participants",
)
router.register(
    r"sites",
    home_rest.SiteViewSet,
    basename="sites",
)

# addressbook
router.register(
    r"addressbook/organizationgroups",
    addressbook_rest.OrganizationGroupViewSet,
    basename="api-addressbook-organization-group",
)
router.register(
    r"addressbook/organizations",
    addressbook_rest.OrganizationViewSet,
    basename="api-addressbook-organization",
)
router.register(
    r"addressbook/contacts",
    addressbook_rest.ContactViewSet,
    basename="api-addressbook-contact",
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
    # path(
    #     "projects/my_departments",
    #     projects_rest.ProjectDepartmentList.as_view(),
    #     name="projects-list-my-departments",
    # ),
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

tasks_urls = [
    path(
        "projects/<int:project_id>/tasks/acra/ask/",
        tasks_acra_proxy.AcraAskView.as_view(),
        name="tasks-acra-ask",
    ),
    path(
        "projects/<int:project_id>/tasks/acra/co-recommendations/",
        tasks_acra_proxy.AcraCoRecommendationsView.as_view(),
        name="tasks-acra-co-recommendations",
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
    path(
        "survey/questions/",
        survey_rest.SurveyQuestionsView.as_view(),
        name="api-survey-questions",
    ),
]


def _collect_plugin_rest_urls():
    from recoco.apps.plugins.manager import get_plugin_manager

    urls = []
    pm = get_plugin_manager()
    for _name, plugin in pm.list_name_plugin():
        rest_mod_name = getattr(plugin, "rest_urls_module", None)
        if not rest_mod_name:
            continue
        try:
            mod = importlib.import_module(rest_mod_name)
            urls.extend(getattr(mod, "urlpatterns", []))
        except ImportError:
            pass
    return urls


urlpatterns = (
    router.urls
    + api_urls
    + auth_urls
    + tasks_urls
    + survey_urls
    + _collect_plugin_rest_urls()
)
