# encoding: utf-8

"""
views to fill surveys

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-03 14:26:39 CEST
"""

from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from .. import forms, models

#####
# Session
#####


class SessionDetailsView(DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    context_object_name = "session"
    template_name = "survey/session_details.html"


class SessionDoneView(DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    template_name = "survey/session_done.html"


#####
# Questions
#####


def survey_question_details(request, session_id, question_id):
    """Display a single question and go to next"""
    session = get_object_or_404(models.Session, pk=session_id)
    question = get_object_or_404(models.Question, pk=question_id)
    try:
        answer = models.Answer.objects.get(question=question, session=session)
    except models.Answer.DoesNotExist:
        answer = None

    if request.method == "POST":
        form = forms.AnswerForm(question, answer, request.POST)
        if form.is_valid():
            form.update_session(session)
            return redirect(
                "survey-question-next", session_id=session_id, question_id=question_id
            )
    else:
        form = forms.AnswerForm(question, answer)

    return render(request, "survey/question_details.html", locals())


def survey_next_question(request, session_id, question_id=None):
    """Redirect to next unanswered/answerable question from survey"""
    session = get_object_or_404(models.Session, pk=session_id)

    if question_id is not None:
        question = get_object_or_404(models.Question, pk=question_id)
        next_question = session.next_question(question)
    else:
        next_question = session.next_question()

    if next_question:
        # redirect to question
        return redirect(
            "survey-question-details",
            session_id=session.id,
            question_id=next_question.id,
        )
    # we're done
    return redirect("survey-session-done", session_id=session.pk)


def survey_previous_question(request, session_id, question_id):
    """Redirect to previous unanswered/answerable question from survey"""
    session = get_object_or_404(models.Session, pk=session_id)
    question = get_object_or_404(models.Question, pk=question_id)

    previous_question = session.previous_question(question)
    if previous_question:
        # redirect to question
        return redirect(
            "survey-question-details",
            session_id=session.id,
            question_id=previous_question.id,
        )
    # go back to survey
    return redirect("survey-session-details", session_id=session.pk)


# eof
