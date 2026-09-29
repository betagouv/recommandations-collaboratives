from . import common
from .development import *  # noqa: F403

DS_AUTOLOAD_SCHEMA = False
CELERY_TASK_ALWAYS_EAGER = True

CONTENT_SECURITY_POLICY = common.CONTENT_SECURITY_POLICY
