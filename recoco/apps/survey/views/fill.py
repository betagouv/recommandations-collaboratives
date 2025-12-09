# encoding: utf-8

"""
views to fill surveys

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-03 14:26:39 CEST
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.sites.models import Site
from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView, RedirectView

from recoco.apps.projects import models as projects_models
from recoco.apps.projects.utils import reactivate_if_necessary
from recoco.utils import has_perm, has_perm_or_403

from .. import forms, models, signals

#####
# Session
#####


class SessionDetailsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    context_object_name = "session"
    template_name = "survey/session_details.html"

    def has_permission(self):
        object = self.get_object()
        return has_perm(self.request.user, "projects.use_surveys", object.project)


class SessionResultsView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = models.Session
    pk_url_kwarg = "session_id"
    context_object_name = "session"
    template_name = "survey/session_results.html"

    def has_permission(self):
        object = self.get_object()
        return has_perm(self.request.user, "projects.use_surveys", object.project)


class SessionDoneView(LoginRequiredMixin, PermissionRequiredMixin, RedirectView):
    permanent = False
    query_string = True
    pattern_name = "projects-project-detail-knowledge"

    def get_redirect_url(self, *args, **kwargs):
        session = get_object_or_404(models.Session, pk=kwargs["session_id"])
        project = get_object_or_404(projects_models.Project, pk=session.project.id)
        return super().get_redirect_url(*args, project_id=project.id)


#####
# Questions
#####


@login_required
def survey_question_details(request, session_id, question_id):
    """Display a single question and go to next"""
    session = get_object_or_404(
        models.Session,
        pk=session_id,
    )
    question = get_object_or_404(models.Question, pk=question_id)
    try:
        answer = models.Answer.objects.get(question=question, session=session)
    except models.Answer.DoesNotExist:
        answer = None

    has_perm_or_403(request.user, "projects.use_surveys", session.project)

    if request.method == "POST":
        form = forms.AnswerForm(question, answer, request.POST, files=request.FILES)
        if form.is_valid():
            form.update_session(session, request.user)

            reactivate_if_necessary(session.project, request.user)

            signals.survey_session_updated.send(
                sender=survey_question_details,
                session=session,
                request=request,
            )

            return redirect(
                "survey-question-next", session_id=session_id, question_id=question_id
            )
    else:
        form = forms.AnswerForm(question, answer)

    return render(request, "survey/question_details.html", locals())


@login_required
def survey_create_session_for_project(request, project_id, site_id=None):
    """
    Create a session for the given project if necessary. Redirects to session.
    Optional survey_id allows one to ask for another survey in case of multisites
    """
    project = get_object_or_404(
        projects_models.Project, sites=request.site, pk=project_id
    )

    has_perm_or_403(request.user, "projects.use_surveys", project)

    site_config = request.site_config

    if site_id:
        try:
            try:
                site = project.sites.get(id=site_id)
            except Site.DoesNotExist as _:
                raise BadRequest("Project not on site") from None
            survey = site.configuration.project_survey
        except models.Survey.DoesNotExist as _:
            raise BadRequest("Unknown survey") from None
    else:
        survey = site_config.project_survey

    session, _ = models.Session.objects.get_or_create(project=project, survey=survey)
    signals.survey_session_started.send(
        sender=None, survey=survey, project=project, request=request
    )

    url = reverse("survey-session-start", args=(session.id,))
    if "first_time" in request.GET:
        url += "?first_time=1"

    return redirect(url)


@login_required
def survey_next_question(request, session_id, question_id=None):
    """Redirect to next unanswered/answerable question from survey"""
    session = get_object_or_404(models.Session, pk=session_id)
    has_perm_or_403(request.user, "projects.use_surveys", session.project)

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


@login_required
def survey_previous_question(request, session_id, question_id):
    """Redirect to previous unanswered/answerable question from survey"""
    session = get_object_or_404(models.Session, pk=session_id)
    question = get_object_or_404(models.Question, pk=question_id)

    has_perm_or_403(request.user, "projects.use_surveys", session.project)

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
    session = get_object_or_404(
        models.Session, survey__site=request.site, pk=session_id
    )

    has_perm_or_403(request.user, "sites.manage_surveys", request.site)

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
