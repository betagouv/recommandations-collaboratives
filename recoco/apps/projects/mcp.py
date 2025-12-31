#!/usr/bin/env python

#!/usr/bin/env python

from mcp_server import MCPToolset, drf_serialize_output

from .models import Project
from .serializers import ProjectSummarySerializer


class ProjectQueryTool(MCPToolset):
    """Obtient des informations sur les projets"""

    @drf_serialize_output(ProjectSummarySerializer)
    def get_project(self, id):
        """Récupère le contenu détaillé d'un projet"""
        return Project.objects.prefetch_related(
            "survey_session",
            "survey_session__survey",
            "survey_session__survey__question_sets",
            "survey_session__survey__question_sets__questions",
        ).get(pk=id)
