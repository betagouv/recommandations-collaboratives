from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from . import models
from .forms import AnswerForm


def survey_question_details(request, session_id, question_id):
    """Display a single question"""
    session = get_object_or_404(models.Session, pk=session_id)
    question = get_object_or_404(models.Question, pk=question_id)

    if request.method == "POST":
        form = AnswerForm(question, request.POST)
        if form.is_valid():
            form.update_session(session)
            next_question = question.next()
            if not next_question:
                # Next QuestionSet?
                next_question_set = question.question_set.next()
                if next_question_set:
                    next_question = next_question_set.first_question()

            if next_question:
                # Next question in same QuestionSet
                return redirect(
                    "survey-question-details",
                    session_id=session.pk,
                    question_id=next_question.pk,
                )
            else:
                # Nothing more, send to results?
                return redirect("survey-session-done", session_id=session.pk)
    else:
        form = AnswerForm(question)

    return render(request, "survey/question_details.html", locals())


class SessionDoneView(DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    template_name = "survey/session/done.html"
