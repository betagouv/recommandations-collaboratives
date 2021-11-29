from urbanvitaliz.utils import check_if_switchtender

from .models import Project
from .utils import get_active_project


def is_switchtender_processor(request):
    return {"is_switchtender": check_if_switchtender(request.user)}


def active_project_processor(request):
    return {"active_project": get_active_project(request)}
