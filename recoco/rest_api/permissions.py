from rest_framework.permissions import SAFE_METHODS, BasePermission

from recoco.apps.projects import models as projects_models
from recoco.utils import has_perm, is_staff_for_site


class IsStaffForSite(BasePermission):
    def has_permission(self, request, view):
        return request.user and is_staff_for_site(user=request.user, site=request.site)


class IsStaffForSiteOrReadOnly(IsStaffForSite):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or super().has_permission(request, view)


class IsStaffForSiteOrIsAuthenticatedReadOnly(IsStaffForSite):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            and request.user
            and request.user.is_authenticated
        ) or super().has_permission(request, view)


class IsM2MPartner(BasePermission):
    """Only allow the m2m partners of the current site"""

    message = "Vous n'êtes pas autorisé à utiliser l'API machine à machine."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and has_perm(request.user, "sites.use_m2m_api", request.site)
        )


class BaseConversationPermission(BasePermission):
    def has_permission(self, request, view):
        project = projects_models.Project.objects.get(pk=view.kwargs["project_id"])
        if request.method in SAFE_METHODS:
            return has_perm(request.user, "projects.view_public_notes", project)
        return has_perm(request.user, "projects.use_public_notes", project)
