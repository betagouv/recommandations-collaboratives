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
        return Project.objects.get(pk=id)
