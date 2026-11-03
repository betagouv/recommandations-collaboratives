from django.conf import settings
from django.http import HttpRequest

from recoco import __version__


def embed(request: HttpRequest) -> dict:
    return {"is_embedded": getattr(request, "is_embedded", False)}


def sentry_frontend(request: HttpRequest) -> dict:
    if settings.DEBUG:
        return {}

    config = {
        "dsn": settings.SENTRY_FRONTEND_DSN,
        "release": f"recoco@{__version__}",
    }
    if request.user.is_authenticated:
        config["userId"] = request.user.id
    return {"sentry_frontend_config": config}
