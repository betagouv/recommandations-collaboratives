from django.conf import settings
from django.http import HttpRequest

from recoco import __version__


def embed(request: HttpRequest) -> dict:
    return {"is_embedded": getattr(request, "is_embedded", False)}


def sentry_frontend(request: HttpRequest) -> dict:
    if not settings.SENTRY_FRONTEND_DSN:
        return {}

    config = {
        "dsn": settings.SENTRY_FRONTEND_DSN,
        "environment": settings.SENTRY_FRONTEND_ENVIRONMENT,
        "release": f"recoco@{__version__}",
        "tracesSampleRate": settings.SENTRY_FRONTEND_TRACES_SAMPLE_RATE,
    }
    if request.user.is_authenticated:
        config["userId"] = request.user.id
    return {"sentry_frontend_config": config}
