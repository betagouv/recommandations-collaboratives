# encoding: utf-8

"""
views to fill surveys

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-03 14:26:39 CEST
"""

from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from django.views.generic import DetailView

from .. import models
from .. import forms

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
            next_question = question.next()
            if not next_question:
                # Next QuestionSet?
                next_question_set = question.question_set.next()
                if next_question_set:
                    # Next Question in next Question Set
                    next_question = next_question_set.first_question()

            if next_question:
                # Next Question please
                return redirect(
                    "survey-question-details",
                    session_id=session.pk,
                    question_id=next_question.pk,
                )
            else:
                # Nothing more, send to done page
                return redirect("survey-session-done", session_id=session.pk)
    else:
        form = forms.AnswerForm(question, answer)

    return render(request, "survey/question_details.html", locals())


# eof
