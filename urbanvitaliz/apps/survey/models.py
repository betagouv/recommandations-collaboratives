from django.db import models
from django.urls import reverse


class Survey(models.Model):
    pass


class QuestionSet(models.Model):
    """A set of question (ex: same topic)"""

    survey = models.ForeignKey(
        Survey, related_name="question_sets", on_delete=models.CASCADE
    )

    heading = models.CharField(max_length=255)
    subheading = models.TextField()

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

    def __str__(self):
        return self.heading


class Question(models.Model):
    # tags_required =
    question_set = models.ForeignKey(
        QuestionSet, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=255)

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

    def __str__(self):
        return self.text


class Choice(models.Model):  # ManyToOne?
    class Meta:
        unique_together = [["value", "question"]]

    value = models.CharField(max_length=30)
    text = models.CharField(max_length=255)
    # tags =

    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )


class Session(models.Model):
    """A pausable user session with checkpoint for resuming"""

    pass


class Answer(models.Model):
    """Actual answer to a question"""

    session = models.ForeignKey(
        Session, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    value = models.CharField(max_length=30)
    # tags =
