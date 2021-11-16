from urbanvitaliz.utils import check_if_switchtender


def is_switchtender_processor(request):
    return {"is_switchtender": check_if_switchtender(request.user)}
