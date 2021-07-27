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
        self.question = question
        super().__init__(*args, **kwargs)

        choices = []
        for choice in question.choices.all():
            choices.append((choice.value, choice.text))
        self.fields["answer"].choices = choices

    def update_session(self, session: models.Session):
        answer_value = self.cleaned_data.get("answer")
        answer, created = models.Answer.objects.get_or_create(
            session=session,
            question=self.question,
            defaults={"value": answer_value},
        )
        if not created:
            answer.value = answer_value
            answer.save()

        return True
