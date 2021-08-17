import math

from django import template

from ..models import Answer, Choice, Question

register = template.Library()


@register.simple_tag
def question_set_completion(session, question_set):
    """Return an optimistic percentage of completion for a question_set"""
    answer_count = Answer.objects.filter(
        session=session, question__question_set=question_set
    ).count()
    question_count = Question.objects.filter(
        question_set=question_set, precondition=""
    ).count()

    return min(math.ceil(answer_count / question_count * 100), 100)


@register.simple_tag
def lookup_choices_from_answer(answer):
    """Return the choice object from an answer (rehydration)"""
    choices = []

    # XXX keep that?
    if type(answer.values) is not list:
        answer.values = [answer.values]

    for value in answer.values:
        try:
            choices.append(Choice.objects.get(value=value, question=answer.question))
        except Choice.DoesNotExist:
            pass

    return choices
