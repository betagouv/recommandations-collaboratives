import math

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
