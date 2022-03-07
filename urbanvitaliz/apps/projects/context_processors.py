from urbanvitaliz.utils import check_if_switchtender

from .utils import (can_administrate_project, can_manage_project,
                    get_active_project)


def is_switchtender_processor(request):
    return {"is_switchtender": check_if_switchtender(request.user)}


def active_project_processor(request):
    active_project = get_active_project(request)
    context = {
        "active_project": active_project,
    }

    if active_project:
        context.update(
            {
                "active_project_can_manage": can_manage_project(
                    active_project, request.user
                ),
                "active_project_can_administrate": can_administrate_project(
                    active_project, request.user
                ),
            }
        )

    return context
