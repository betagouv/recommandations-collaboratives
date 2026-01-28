from django import template

from .. import utils
from ..models import Answer, Choice, Session

register = template.Library()


@register.simple_tag
def question_set_completion(session, question_set):
    return utils.compute_qs_completion(session, question_set)


@register.simple_tag
def question_set_visible(session, question_set):
    return question_set.check_precondition(session)


@register.simple_tag
def question_answer_visible(session, question):
    return question.check_precondition(session)


@register.simple_tag
def question_answer(session, question):
    try:
        return Answer.objects.get(question=question, session=session)
    except Answer.DoesNotExist:
        return None


@register.simple_tag
def lookup_choices_from_answer(answer):
    """Return the choice object from an answer (rehydration)"""
    if not answer:
        return
    choices = []

    # XXX keep that?
    if not isinstance(answer.values, list):
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


@register.simple_tag
def project_session_for_survey(project, survey):
    try:
        return Session.objects.get(project=project, survey=survey)
    except Session.DoesNotExist:
        return None
