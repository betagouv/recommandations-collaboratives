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

        choices = [(choice.value, choice.text) for choice in question.choices.all()]

        if choices:
            self.fields["answer"] = (
                forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
                if question.is_multiple
                else forms.ChoiceField(widget=forms.RadioSelect())
            )

            self.fields["answer"].choices = choices
        else:
            # No choices, force comment to be mandatory since this is our
            # expected answer
            self.fields["comment"].required = True

        if question.upload_title:
            self.fields["attachment"] = forms.FileField(required=False)

        # If we already have an answer, prefill
        if answer:
            if "answer" in self.fields:
                if not question.is_multiple:
                    if isinstance(answer.values, list):
                        initial_value = answer.values[0]
                    else:
                        # Compatibility with old way of storing
                        initial_value = answer.values
                else:
                    initial_value = answer.values
                self.fields["answer"].initial = initial_value
            self.fields["comment"].initial = answer.comment
            if "attachment" in self.fields:
                self.fields["attachment"].initial = answer.attachment

    def update_session(self, session: models.Session):
        answer_values = self.cleaned_data.get("answer", "")
        comment = self.cleaned_data.get("comment", None)
        attachment = self.cleaned_data.get("attachment", None)

        # compute the signals according to the kind of question
        if not isinstance(answer_values, list):
            answer_values = (answer_values,)

        # multiple choices
        choices = models.Choice.objects.filter(
            question=self.question, value__in=answer_values
        )
        signals = ""
        choice_signals = []
        for choice in choices:
            choice_signals.append(choice.signals)
        signals = ", ".join(choice_signals)

        answer, created = models.Answer.objects.get_or_create(
            session=session,
            question=self.question,
            defaults={
                "values": answer_values,
                "comment": comment,
                "signals": signals,
                "attachment": attachment,
            },
        )
        if not created:
            answer.values = answer_values
            answer.comment = comment
            answer.signals = signals
            answer.attachment = attachment
            answer.save()

        answer.choices.set(choices)

        return True


# editor forms


class EditQuestionSetForm(forms.ModelForm):
    """Create and update form for question_sets"""

    class Meta:
        model = models.QuestionSet
        fields = ["priority", "heading", "icon", "color", "subheading"]


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
            "text_short",
            "precondition",
            "why",
            "how",
            "upload_title",
            "comment_title",
        ]


class EditChoiceForm(forms.ModelForm):
    """Create and update form for choices"""

    class Meta:
        model = models.Choice
        fields = ["text", "value", "conclusion", "signals", "priority"]
