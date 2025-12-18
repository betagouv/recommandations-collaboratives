#!/usr/bin/env python

from mcp_server import MCPToolset

from .models import Resource
from .serializers import ResourceDetailSerializer, ResourceSerializer


class ResourceQueryTool(MCPToolset):
    """Recherche dans les ressources d'UrbanVitaliz"""

    def search_resources(self, text) -> list[dict]:
        """Rechercher des fiches ressources"""
        serializer = ResourceSerializer(Resource.search(text), many=True)
        return serializer.data

    def get_resource(self, id):
        """Récupère le contenu détaillé d'une ressource en fournissant son ID de base de données."""
        return ResourceDetailSerializer(Resource.objects.get(pk=id)).data
