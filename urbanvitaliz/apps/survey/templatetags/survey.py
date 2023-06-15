from django import template

from .. import utils
from ..models import Choice

register = template.Library()


@register.simple_tag
def question_set_completion(session, question_set):
    return utils.compute_qs_completion(session, question_set)


@register.simple_tag
def lookup_choices_from_answer(answer):
    """Return the choice object from an answer (rehydration)"""
    choices = []

    # XXX keep that?
    if type(answer.values) is not list:
        answer.values = [answer.values]

    # FIXME add a test and then a single request for all choices like
    # Choice.objects.filter(question=answer.question, value__in=answer.values)
    # could it be computed on the view instead of the tag itself ?
    for value in answer.values:
        try:
            choices.append(Choice.objects.get(value=value, question=answer.question))
        except Choice.DoesNotExist:
            pass

    return choices
