# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-27 11:33:08 CEST
"""

from django import forms

from . import models


class AnswerForm(forms.Form):
    answer = forms.ChoiceField(widget=forms.RadioSelect())

    def __init__(self, question: models.Question, *args, **kwargs):
        super().__init__(*args, **kwargs)

        choices = []
        for choice in question.choices.all():
            choices.append((choice.value, choice.text))
        self.fields["answer"].choices = choices
