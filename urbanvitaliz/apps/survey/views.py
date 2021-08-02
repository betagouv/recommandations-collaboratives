from django.urls import reverse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from . import models
from . import forms

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


########################################################################
# Administration views
########################################################################


#
# survey views


@login_required
def editor_survey_details(request, survey_id=None):
    """List question sets for given survey"""
    survey = get_object_or_404(models.Survey, pk=survey_id)
    return render(request, "survey/editor/survey/details.html", locals())


#
# question_set views


@login_required
def editor_question_set_details(request, question_set_id=None):
    """Return the details of given question_set"""
    question_set = get_object_or_404(models.QuestionSet, pk=question_set_id)
    return render(request, "survey/question_set/details.html", locals())


@login_required
def editor_question_set_update(request, question_set_id=None):
    """Update informations for question_set"""
    question_set = get_object_or_404(models.QuestionSet, pk=question_set_id)
    if request.method == "POST":
        form = forms.EditQuestionSetForm(request.POST, instance=question_set)
        if form.is_valid():
            form.save()
            next_url = reverse("survey-question-set-details", args=[question_set.id])
            return redirect(next_url)
    else:
        form = forms.EditQuestionSetForm(instance=question_set)
    return render(request, "survey/question_set/update.html", locals())


@login_required
def editor_question_set_create(request, survey_id=None):
    """Create new question_set"""
    survey = get_object_or_404(models.Survey, pk=survey_id)
    if request.method == "POST":
        form = forms.EditQuestionSetForm(request.POST)
        if form.is_valid():
            question_set = form.save()
            next_url = reverse("survey-question-set-details", args=[question_set.id])
            return redirect(next_url)
    else:
        form = forms.EditQuestionSetForm()
    return render(request, "survey/question_set/create.html", locals())


@login_required
def editor_question_set_delete(request, question_set_id=None):
    """Delete question_set (mark as deleted)"""
    question_set = get_object_or_404(models.QuestionSet, pk=question_set_id)
    next_url = reverse("survey-survey-details", question_set.survey_id)
    if request.method == "POST":
        question_set.deleted = timezone.now()
        question_set.save()
        return redirect(next_url)
    return render(request, "survey/editor/question_set/delete.html", locals())


#
# question views


@login_required
def editor_question_details(request, question_id=None):
    """Return the details of given question"""
    question = get_object_or_404(models.Question, pk=question_id)
    return render(request, "survey/question/details.html", locals())


@login_required
def editor_question_update(request, question_id=None):
    """Update informations for question"""
    question = get_object_or_404(models.Question, pk=question_id)
    if request.method == "POST":
        form = forms.EditQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            next_url = reverse("survey-question-details", args=[question.id])
            return redirect(next_url)
    else:
        form = forms.EditQuestionForm(instance=question)
    return render(request, "survey/question/update.html", locals())


@login_required
def editor_question_create(request, question_set_id=None):
    """Create new question"""
    question_set = get_object_or_404(models.QuestionSet, pk=question_set_id)
    if request.method == "POST":
        form = forms.EditQuestionForm(request.POST)
        if form.is_valid():
            question = form.save()
            next_url = reverse("survey-question-details", args=[question.id])
            return redirect(next_url)
    else:
        form = forms.EditQuestionForm()
    return render(request, "survey/question/create.html", locals())


@login_required
def editor_question_delete(request, question_id=None):
    """Delete question (mark as deleted)"""
    question = get_object_or_404(models.Question, pk=question_id)
    next_url = reverse("survey-question-set-details", question.question_set_id)
    if request.method == "POST":
        question.deleted = timezone.now()
        question.save()
        return redirect(next_url)
    return render(request, "survey/editor/question/delete.html", locals())


#
# choice views


@login_required
def editor_choice_update(request, choice_id=None):
    """Update informations for choice"""
    choice = get_object_or_404(models.Choice, pk=choice_id)
    if request.method == "POST":
        form = forms.EditChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            next_url = reverse("survey-question-details", args=[choice.question_id])
            return redirect(next_url)
    else:
        form = forms.EditChoiceForm(instance=choice)
    return render(request, "survey/choice/update.html", locals())


@login_required
def editor_choice_create(request, choice_id=None):
    """Create new choice"""
    choice = get_object_or_404(models.Choice, pk=choice_id)
    if request.method == "POST":
        form = forms.EditChoiceForm(request.POST)
        if form.is_valid():
            form.save()
            next_url = reverse("survey-question-details", args=[choice.question_id])
            return redirect(next_url)
    else:
        form = forms.EditChoiceForm()
    return render(request, "survey/choice/create.html", locals())


@login_required
def editor_choice_delete(request, choice_id=None):
    """Delete choice (mark as deleted)"""
    choice = get_object_or_404(models.Choice, pk=choice_id)
    next_url = reverse("survey-question-details", choice.question_id)
    if request.method == "POST":
        choice.deleted = timezone.now()
        choice.save()
        return redirect(next_url)
    return render(request, "survey/editor/choice/delete.html", locals())


# eof
