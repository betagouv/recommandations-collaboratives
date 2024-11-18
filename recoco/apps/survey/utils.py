import math

from django.db.models import Q

from . import models


def compute_qs_completion(session, question_set):
    """Return an optimistic percentage of completion for a question_set"""
    signals = session.signals

    answer_count = models.Answer.objects.filter(
        session=session, question__question_set=question_set
    ).count()

    question_count = (
        models.Question.objects.filter(question_set=question_set)
        .filter(Q(precondition__in=signals) | Q(precondition=""))
        .count()
    )

    if question_count == 0:
        return 0

    return min(math.ceil(answer_count / question_count * 100), 100)
