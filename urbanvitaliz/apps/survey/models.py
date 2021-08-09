from django.db import models
from tagging.fields import TagField
from tagging.models import Tag
from tagging.registry import register as tagging_register


class Survey(models.Model):
    name = models.CharField(max_length=80)


class QuestionSet(models.Model):
    """A set of question (ex: same topic)"""

    survey = models.ForeignKey(
        Survey, related_name="question_sets", on_delete=models.CASCADE
    )

    heading = models.CharField(max_length=255, verbose_name="En-tête")
    icon = models.CharField(max_length=80, verbose_name="Icône", blank=True)

    subheading = models.TextField(verbose_name="Sous-titre")

    deleted = models.DateTimeField(null=True)

    def _following(self, order_by):
        """return the following question set defined by the given order_by"""
        question_sets = self.survey.question_sets

        iterator = question_sets.order_by(order_by).iterator()
        for question_set in iterator:
            if question_set == self:
                try:
                    return next(iterator)
                except StopIteration:
                    return None

        return None

    def next(self):
        """Return the next question set"""
        return self._following(order_by="id")

    def previous(self):
        """Return the previous question set"""
        return self._following(order_by="-id")

    def first_question(self):
        for question in self.questions.all():
            return question

        return None

    def __str__(self):
        return self.heading


class Question(models.Model):
    """A question with mutliple choices"""

    precondition = TagField(
        verbose_name="Pré-condition",
        help_text="Affiche cette question si TOUS les signaux saisis sont émis",
    )

    question_set = models.ForeignKey(
        QuestionSet, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=255, verbose_name="Texte de la question")

    deleted = models.DateTimeField(null=True)

    def _following(self, order_by):
        """return the following question defined by the given order_by"""
        questions = self.question_set.questions

        iterator = questions.order_by(order_by).iterator()
        for question in iterator:
            if question == self:
                try:
                    return next(iterator)
                except StopIteration:
                    return None

        return None

    def next(self):
        """Return the next question"""
        return self._following(order_by="id")

    def previous(self):
        """Return the previous question"""
        return self._following(order_by="-id")

    def check_precondition(self, session: "Session"):
        """Return true if the precondition is met"""
        my_tags = set(self.precondition_tags.values_list("name", flat=True))
        return my_tags.issubset(session.signals)

    def __str__(self):
        return self.text


tagging_register(
    Question,
    tag_descriptor_attr="precondition_tags",
    tagged_item_manager_attr="precondition_tagged",
)


class Choice(models.Model):
    """A choice for a given Question"""

    class Meta:
        unique_together = [["value", "question"]]

    value = models.CharField(max_length=30)
    signals = TagField(verbose_name="Signaux")
    text = models.CharField(max_length=255)

    deleted = models.DateTimeField(null=True)

    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )


tagging_register(Choice, tag_descriptor_attr="tags")


class Session(models.Model):
    """A pausable user session with checkpoint for resuming"""

    survey = models.ForeignKey(
        Survey, related_name="sessions", on_delete=models.CASCADE
    )

    @property
    def signals(self):
        """Return the union of signals from Answers of this Session"""
        return {
            tag.name
            for tag in Tag.objects.usage_for_queryset(
                Answer.objects.filter(session=self.pk)
            )
        }

    def next_question(self):
        """Return the first unanswered question"""
        answered_questions = Answer.objects.filter(session=self).values_list(
            "question__id", flat=True
        )

        for qs in self.survey.question_sets.all():
            for question in qs.questions.all():
                if question.id not in answered_questions:
                    return question

        return None

    def first_question(self):
        """Return the first Question of the first Question Set"""
        for qs in self.survey.question_sets.all():
            for question in qs.questions.all():
                return question

        return None

    def __str__(self):
        return "Session #{0}".format(self.id)


class Answer(models.Model):
    """Actual answer to a question"""

    class Meta:
        unique_together = (("session", "question"),)

    session = models.ForeignKey(
        Session, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=30)
    signals = TagField(verbose_name="Signaux", blank=True, null=True)
    comment = models.TextField(blank=True)


tagging_register(Answer, tag_descriptor_attr="tags")
