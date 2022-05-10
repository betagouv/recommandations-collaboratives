import math

from django.core.exceptions import ImproperlyConfigured
from urbanvitaliz.apps.home.models import SiteConfiguration

from . import models


def compute_qs_completion(session, question_set):
    """Return an optimistic percentage of completion for a question_set"""
    answer_count = models.Answer.objects.filter(
        session=session, question__question_set=question_set
    ).count()
    question_count = models.Question.objects.filter(
        question_set=question_set, precondition=""
    ).count()

    if question_count == 0:
        return 0

    return min(math.ceil(answer_count / question_count * 100), 100)


def get_site_config_or_503(site):
    try:
        return SiteConfiguration.objects.get(site=site)
    except SiteConfiguration.DoesNotExist:
        raise ImproperlyConfigured(
            "Please create a SiteConfiguration before using this feature",
        )
