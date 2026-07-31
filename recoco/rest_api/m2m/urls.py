from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from recoco.apps.projects.views import rest as projects_rest
from recoco.rest_api.permissions import IsM2MPartner

app_name = "m2m"

api_urls = [
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

# Restrict the schema to the m2m endpoints only, mounted under their real
# prefix so generated paths match the ones clients actually call.
schema_urlconf = [path("api/m2m/", include((api_urls, app_name)))]

schema_urls = [
    path(
        "schema/",
        SpectacularAPIView.as_view(
            permission_classes=[IsM2MPartner],
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
        SpectacularSwaggerView.as_view(
            permission_classes=[IsM2MPartner], url_name="m2m:schema"
        ),
        name="swagger-ui",
    ),
]

urlpatterns = api_urls + schema_urls
