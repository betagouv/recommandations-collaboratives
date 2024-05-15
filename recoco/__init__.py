VERSION = "2.28.0"

from .worker import app as celery_app

__all__ = ("celery_app",)
