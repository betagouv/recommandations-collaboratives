from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from recoco.apps.projects.views import rest as projects_rest
from recoco.rest_api.permissions import IsM2MPartner

app_name = "m2m"


class M2MAPIRootView(routers.APIRootView):
    """List the endpoints of the m2m api"""

    permission_classes = [IsM2MPartner]


class M2MRouter(routers.DefaultRouter):
    """Router whose root view is restricted to the m2m partners, as the rest"""

    APIRootView = M2MAPIRootView


router = M2MRouter()


m2m_urls = [
    path(
        "projects/",
        projects_rest.ProjectCreate.as_view(),
        name="projects-create",
    ),
    path(
        "projects/<int:pk>/members/",
        projects_rest.ProjectMembershipCreate.as_view(),
        name="projects-members-create",
    ),
]

api_urls = router.urls + m2m_urls

# Restrict the schema to the m2m endpoints only, mounted under their real
# prefix so generated paths match the ones clients actually call.
schema_urlconf = [path("api/m2m/", include((api_urls, app_name)))]

schema_urls = [
    path(
        "schema/",
        SpectacularAPIView.as_view(
            urlconf=schema_urlconf,
            custom_settings={
                "TITLE": "Recoco M2M API",
                "DESCRIPTION": "Machine-to-machine API for Recoco integrations.",
                "VERSION": "1.0.0",
            },
        ),
        name="schema",
    ),
    path(
        "schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="m2m:schema"),
        name="swagger-ui",
    ),
]

urlpatterns = api_urls + schema_urls
