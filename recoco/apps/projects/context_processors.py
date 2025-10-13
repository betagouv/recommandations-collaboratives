from collections import defaultdict
from functools import wraps

from django.conf import settings
from django.core.serializers import serialize
from django.utils.timezone import localtime
from notifications import models as notifications_models

from recoco import verbs
from recoco.utils import check_if_advisor, is_admin_for_site, is_staff_for_site

from .utils import can_administrate_project


def exclude_path(excluded_path: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            path_info = request.META["PATH_INFO"]
            if path_info.startswith(excluded_path):
                return {}
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


@exclude_path("/nimda")
def is_switchtender_processor(request):
    return {
        "is_switchtender": check_if_advisor(request.user),
        "is_administrating_project": can_administrate_project(
            project=None, user=request.user
        ),
    }


@exclude_path("/nimda")
@exclude_path("/api")
def unread_notifications_processor(request):
    if not request.user.is_authenticated:
        return {}

    unread_notifications = (
        notifications_models.Notification.on_site.unread()
        .filter(recipient=request.user, public=True)
        .prefetch_related("actor__profile__organization")
        .prefetch_related("action_object")
        .prefetch_related("target")
        .order_by("-timestamp")[:100]
    )

    grouped_notifications = defaultdict(list)

    show_project_verb_list = [
        verbs.Document.ADDED,
        verbs.Document.ADDED_FILE,
        verbs.Document.ADDED_LINK,
        verbs.Recommendation.COMMENTED,
        verbs.Recommendation.CREATED,
        verbs.Conversation.PUBLIC_MESSAGE,
        verbs.Conversation.PRIVATE_MESSAGE,
        verbs.Survey.STARTED,
        verbs.Survey.UPDATED,
    ]

    for notification in unread_notifications:
        date = localtime(notification.timestamp).date()
        grouped_notifications[date].append(notification)

    return {
        "unread_notifications": serialize("json", unread_notifications.all()),
        "unread_notifications_count": unread_notifications.count(),
        "grouped_notifications": dict(grouped_notifications),
        "show_project_verb_list": show_project_verb_list,
    }


@exclude_path("/nimda")
@exclude_path("/api")
def matomo_context_processor(request):
    """
    Context processor that provides a list of sites accessible to the user.
    """
    context = {
        "matomo_url": settings.MATOMO_URL,
        "matomo_site_id": settings.MATOMO_SITE_ID,
    }

    if not request.user.is_authenticated:
        return context

    # Check if the user is authenticated and has a site
    roles = ",".join(
        role
        for role, has_role in {
            "admin": is_admin_for_site(request.user),
            "staff": is_staff_for_site(request.user, request.site),
            "advisor": check_if_advisor(request.user, request.site),
        }.items()
        if has_role
    )

    return {
        **context,
        "matomo_user_roles": roles,
    }


# eof
