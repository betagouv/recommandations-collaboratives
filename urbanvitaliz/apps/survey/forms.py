# encoding: utf-8

"""
Views for resources application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-27 11:33:08 CEST
"""

from django import forms
from markdownx.fields import MarkdownxFormField

from . import models


class AnswerForm(forms.Form):
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(
        self, question: models.Question, answer: models.Answer, *args, **kwargs
    ):
        self.question = question
        super().__init__(*args, **kwargs)

        self.fields["answer"] = (
            forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
            if question.is_multiple
            else forms.ChoiceField(widget=forms.RadioSelect())
        )

        choices = []
        for choice in question.choices.all():
            choices.append((choice.value, choice.text))
        self.fields["answer"].choices = choices

        # If we already have an answer, prefill
        if answer:
            self.fields["answer"].initial = answer.values
            self.fields["comment"].initial = answer.comment

    def update_session(self, session: models.Session):
        answer_values = self.cleaned_data.get("answer")
        comment = self.cleaned_data.get("comment", None)

        # compute the signals according to the kind of question
        if isinstance(answer_values, list):
            # multiple choices
            choices = models.Choice.objects.filter(
                question=self.question, value__in=answer_values
            )
            signals = []
            for choice in choices:
                signals.append(choice.signals)
            signals = ", ".join(signals)
        else:
            # single choice
            choice = models.Choice.objects.get(
                question=self.question, value=answer_values
            )
            signals = choice.signals

        answer, created = models.Answer.objects.get_or_create(
            session=session,
            question=self.question,
            defaults={
                "values": answer_values,
                "comment": comment,
                "signals": signals,
            },
        )
        if not created:
            answer.values = answer_values
            answer.comment = comment
            answer.signals = signals
            answer.save()

        return True


# editor forms


class EditQuestionSetForm(forms.ModelForm):
    """Create and update form for question_sets"""

    class Meta:
        model = models.QuestionSet
        fields = ["heading", "icon", "subheading"]


class EditQuestionForm(forms.ModelForm):
    """Create and update form for questions"""

    why = MarkdownxFormField(required=False)
    how = MarkdownxFormField(required=False)

    class Meta:
        model = models.Question
        fields = [
            "priority",
            "is_multiple",
            "text",
            "precondition",
            "why",
            "how",
            "comment_title",
        ]


class EditChoiceForm(forms.ModelForm):
    """Create and update form for choices"""

    class Meta:
        model = models.Choice
        fields = ["text", "value", "signals"]
