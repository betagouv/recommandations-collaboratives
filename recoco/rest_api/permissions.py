from rest_framework.permissions import SAFE_METHODS, BasePermission

from recoco.utils import is_staff_for_site


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
