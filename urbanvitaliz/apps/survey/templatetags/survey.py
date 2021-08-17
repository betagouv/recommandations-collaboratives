import math

from django import template

from ..models import Answer, Question

register = template.Library()


@register.simple_tag
def question_set_completion(session, question_set):
    answer_count = Answer.objects.filter(
        session=session, question__question_set=question_set
    ).count()
    question_count = Question.objects.filter(
        question_set=question_set, precondition=""
    ).count()

    return min(math.ceil(answer_count / question_count * 100), 100)
