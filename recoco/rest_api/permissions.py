from rest_framework.permissions import SAFE_METHODS, BasePermission

from recoco.apps.projects import models as projects_models
from recoco.utils import has_perm


class BaseConversationPermission(BasePermission):
    def has_permission(self, request, view):
        project = projects_models.Project.objects.get(pk=view.kwargs["project_id"])
        if request.method in SAFE_METHODS:
            return has_perm(request.user, "projects.view_public_notes", project)
        return has_perm(request.user, "projects.use_public_notes", project)
