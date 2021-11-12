# encoding: utf-8

"""
views to fill surveys

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-03 14:26:39 CEST
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.generic import DetailView, RedirectView
from urbanvitaliz.apps.projects import models as projects_models
from urbanvitaliz.utils import is_staff_or_403

from .. import forms, models, signals

#####
# Session
#####


class SessionDetailsView(DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    context_object_name = "session"
    template_name = "survey/session_details.html"


class SessionResultsView(DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    context_object_name = "session"
    template_name = "survey/session_results.html"


class SessionDoneView(RedirectView):
    permanent = False
    query_string = True
    pattern_name = "projects-project-detail"

    def get_redirect_url(self, *args, **kwargs):
        session = get_object_or_404(models.Session, pk=kwargs["session_id"])
        project = get_object_or_404(projects_models.Project, pk=session.project.id)
        return super().get_redirect_url(*args, project_id=project.id)


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
        form = forms.AnswerForm(question, answer, request.POST, request.FILES)
        if form.is_valid():
            form.update_session(session)
            return redirect(
                "survey-question-next", session_id=session_id, question_id=question_id
            )
    else:
        form = forms.AnswerForm(question, answer)

    return render(request, "survey/question_details.html", locals())


def survey_create_session_for_project(request, project_id):
    """Create a session for the given project if necessary. Redirects to
    session."""
    project = get_object_or_404(projects_models.Project, pk=project_id)
    survey = get_object_or_404(models.Survey, pk=1)  # XXX Hardcoded survey ID

    session, created = models.Session.objects.get_or_create(
        project=project, survey=survey
    )

    signals.survey_started.send(
        sender=None, survey=survey, project=project, request=request
    )

    url = reverse("survey-session-start", args=(session.id,))
    if "first_time" in request.GET:
        url += "?first_time=1"

    return redirect(url)


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
        url = reverse("survey-question-details", args=(session.id, next_question.id))
        if "first_time" in request.GET:
            url += "?first_time=1"

        return redirect(url)

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


# Admin Tasks
@login_required
def survey_signals_refresh(request, session_id):
    """Refresh a given session with new signals, on request"""

    is_staff_or_403(request.user)
    session = get_object_or_404(models.Session, pk=session_id)

    update_count = 0
    for answer in session.answers.all():
        if not answer.choices:
            continue

        choice_signals = []
        for choice in answer.choices.all():
            choice_signals.append(choice.signals)

        answer.signals = ", ".join(choice_signals)
        answer.save()

        update_count += 1

    messages.success(
        request, "{0} réponse(s) ont bien été mises à jour.".format(update_count)
    )

    # go back to survey
    return redirect(
        reverse("projects-project-detail", args=(session.project.pk,)) + "#exploration"
    )


# eof
