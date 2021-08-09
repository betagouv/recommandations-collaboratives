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
    comment = forms.CharField(widget=forms.Textarea, required=False)

    def __init__(
        self, question: models.Question, answer: models.Answer, *args, **kwargs
    ):
        self.question = question
        super().__init__(*args, **kwargs)

        choices = []
        for choice in question.choices.all():
            choices.append((choice.value, choice.text))
        self.fields["answer"].choices = choices

        # If we already have an answer, prefill
        if answer:
            self.fields["answer"].initial = answer.value
            self.fields["comment"].initial = answer.comment

    def update_session(self, session: models.Session):
        answer_value = self.cleaned_data.get("answer")
        comment = self.cleaned_data.get("comment", None)

        # We need the Choice object for extra information (such as signals)
        choice = models.Choice.objects.get(question=self.question, value=answer_value)

        answer, created = models.Answer.objects.get_or_create(
            session=session,
            question=self.question,
            defaults={
                "value": answer_value,
                "comment": comment,
                "signals": choice.signals,
            },
        )
        if not created:
            answer.value = answer_value
            answer.comment = comment
            answer.signals = choice.signals
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

    class Meta:
        model = models.Question
        fields = ["priority", "text"]


class EditChoiceForm(forms.ModelForm):
    """Create and update form for choices"""

    class Meta:
        model = models.Choice
        fields = ["text", "value", "signals"]
