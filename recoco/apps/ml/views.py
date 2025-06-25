from django.shortcuts import get_object_or_404

from recoco.apps.resources import models as resources_models


def compare_resource(request, resource_id):
    resource = get_object_or_404(resources_models.Resource, pk=resource_id)
    # 2 summaries diff pour 1 objet donné, non encore présenté.
    return resource
