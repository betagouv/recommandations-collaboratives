# encoding: utf-8

"""
views to fill surveys

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-08-03 14:26:39 CEST
"""

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz.utils import is_staff_or_403

from .. import forms, models

########################################################################
# survey
########################################################################


@login_required
def survey_details(request, survey_id=None):
    """List question sets for given survey"""
    survey = get_object_or_404(models.Survey, site=request.site, pk=survey_id)
    return render(request, "survey/editor/survey/details.html", locals())


########################################################################
# question_set
########################################################################


@login_required
def question_set_details(request, question_set_id=None):
    """Return the details of given question_set"""
    is_staff_or_403(request.user)

    question_set = get_object_or_404(
        models.QuestionSet, survey__site=request.site, pk=question_set_id
    )
    questions = question_set.questions.order_by("-priority")
    return render(request, "survey/editor/question_set/details.html", locals())


@login_required
def question_set_update(request, question_set_id=None):
    """Update informations for question_set"""
    is_staff_or_403(request.user)

    question_set = get_object_or_404(
        models.QuestionSet, survey__site=request.site, pk=question_set_id
    )

    if request.method == "POST":
        form = forms.EditQuestionSetForm(request.POST, instance=question_set)
        if form.is_valid():
            form.save()
            next_url = reverse(
                "survey-editor-question-set-details", args=[question_set.id]
            )
            return redirect(next_url)
    else:
        form = forms.EditQuestionSetForm(instance=question_set)
    return render(request, "survey/editor/question_set/update.html", locals())


@login_required
def question_set_create(request, survey_id=None):
    """Create new question_set"""
    is_staff_or_403(request.user)

    survey = get_object_or_404(models.Survey, site=request.site, pk=survey_id)

    if request.method == "POST":
        form = forms.EditQuestionSetForm(request.POST)
        if form.is_valid():
            question_set = form.save(commit=False)
            question_set.survey = survey
            question_set.save()
            next_url = reverse(
                "survey-editor-question-set-details", args=[question_set.id]
            )
            return redirect(next_url)
    else:
        form = forms.EditQuestionSetForm()
    return render(request, "survey/editor/question_set/create.html", locals())


@login_required
def question_set_delete(request, question_set_id=None):
    """Delete question_set (mark as deleted)"""
    is_staff_or_403(request.user)

    question_set = get_object_or_404(
        models.QuestionSet, survey__site=request.site, pk=question_set_id
    )
    if request.method == "POST":
        question_set.deleted = timezone.now()
        question_set.save()
        next_url = reverse(
            "survey-editor-survey-details", args=[question_set.survey_id]
        )
        return redirect(next_url)
    return render(request, "survey/editor/question_set/delete.html", locals())


#######################################################################
# question
#######################################################################


@login_required
def question_update(request, question_id=None):
    """Update informations for question"""
    is_staff_or_403(request.user)

    question = get_object_or_404(
        models.Question, question_set__survey__site=request.site, pk=question_id
    )
    if request.method == "POST":
        form = forms.EditQuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            next_url = reverse(
                "survey-editor-question-set-details", args=[question.question_set.id]
            )
            return redirect(next_url)
    else:
        form = forms.EditQuestionForm(instance=question)
    return render(request, "survey/editor/question/update.html", locals())


@login_required
def question_create(request, question_set_id=None):
    """Create new question"""
    is_staff_or_403(request.user)

    question_set = get_object_or_404(models.QuestionSet, pk=question_set_id)
    if request.method == "POST":
        form = forms.EditQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.question_set = question_set
            question.save()
            next_url = reverse(
                "survey-editor-question-set-details", args=[question.question_set.id]
            )
            return redirect(next_url)
    else:
        form = forms.EditQuestionForm()
    return render(request, "survey/editor/question/create.html", locals())


@login_required
def question_delete(request, question_id=None):
    """Delete question (mark as deleted)"""
    is_staff_or_403(request.user)

    question = get_object_or_404(
        models.Question, question_set__survey__site=request.site, pk=question_id
    )
    if request.method == "POST":
        question.deleted = timezone.now()
        question.save()
        next_url = reverse(
            "survey-editor-question-set-details", args=[question.question_set.id]
        )
        return redirect(next_url)
    return render(request, "survey/editor/question/delete.html", locals())


#######################################################################
# choice
#######################################################################


@login_required
def choice_update(request, choice_id=None):
    """Update informations for choice"""
    is_staff_or_403(request.user)

    choice = get_object_or_404(
        models.Choice,
        question__question_set__survey__site=get_current_site(request),
        pk=choice_id,
    )
    if request.method == "POST":
        form = forms.EditChoiceForm(request.POST, instance=choice)
        if form.is_valid():
            form.save()
            next_url = reverse(
                "survey-editor-question-set-details",
                args=[choice.question.question_set.id],
            ) + "#q-{0}".format(choice.question.id)
            return redirect(next_url)
    else:
        form = forms.EditChoiceForm(instance=choice)
    return render(request, "survey/editor/choice/update.html", locals())


@login_required
def choice_create(request, question_id=None):
    """Create new choice"""
    is_staff_or_403(request.user)

    question = get_object_or_404(
        models.Question,
        pk=question_id,
        question_set__survey__site=get_current_site(request),
    )
    if request.method == "POST":
        form = forms.EditChoiceForm(request.POST)
        if form.is_valid():
            choice = form.save(commit=False)
            choice.question = question
            choice.save()
            next_url = reverse(
                "survey-editor-question-set-details",
                args=[choice.question.question_set.id],
            )
            return redirect(next_url)
    else:
        form = forms.EditChoiceForm()
    return render(request, "survey/editor/choice/create.html", locals())


@login_required
def choice_delete(request, choice_id=None):
    """Delete choice (mark as delet
    ed)"""
    is_staff_or_403(request.user)

    choice = get_object_or_404(
        models.Choice,
        pk=choice_id,
        question__question_set__survey__site=get_current_site(request),
    )
    if request.method == "POST":
        choice.deleted = timezone.now()
        choice.save()
        next_url = reverse(
            "survey-editor-question-set-details", args=[choice.question.question_set_id]
        )
        return redirect(next_url)
    return render(request, "survey/editor/choice/delete.html", locals())


# eof
