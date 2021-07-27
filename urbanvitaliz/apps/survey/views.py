from django.shortcuts import get_object_or_404, render

from . import models
from .forms import AnswerForm


def survey_question_details(request, question_id):
    """Display a single question"""
    question = get_object_or_404(models.Question, pk=question_id)

    form = AnswerForm(question)

    return render(request, "survey/question_details.html", locals())
