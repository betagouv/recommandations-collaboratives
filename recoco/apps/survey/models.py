import math
import statistics
from datetime import timedelta
from enum import Enum

from autoslug import AutoSlugField
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import cached_property
from markdownx.utils import markdownify
from model_clone import CloneMixin
from tagging.fields import TagField
from tagging.models import Tag
from tagging.registry import register as tagging_register
from taggit.managers import TaggableManager

from recoco.apps.projects import models as projects_models

from . import apps
from .utils import compute_qs_completion


# We need the permission to be associated to the site and not to the surveys
@receiver(post_migrate)
def create_site_permissions(sender, **kwargs):
    if sender.name != apps.SurveyConfig.name:
        return

    site_ct = ContentType.objects.get(app_label="sites", model="site")
    auth_models.Permission.objects.get_or_create(
        codename="manage_surveys",
        name="Can manage the surveys",
        content_type=site_ct,
    )


class DIRECTION(Enum):
    NEXT = "next"
    PREVIOUS = "previous"


class Survey(CloneMixin, models.Model):
    objects = models.Manager()
    on_site = CurrentSiteManager()

    name = models.CharField(max_length=80)

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    _clone_m2o_or_o2m_fields = ["question_sets"]

    def __str__(self):  # pragma: nocover
        return f"Survey: {self.name}"


class QuestionSetManager(models.Manager):
    """Manager for active Question Sets"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class QuestionSet(CloneMixin, models.Model):
    """A set of question (ex: same topic)"""

    objects = QuestionSetManager()
    objects_deleted = models.Manager()

    survey = models.ForeignKey(
        Survey, related_name="question_sets", on_delete=models.CASCADE
    )

    heading = models.CharField(max_length=255, verbose_name="En-tête")
    icon = models.CharField(max_length=80, verbose_name="Icône", blank=True)
    color = models.CharField(
        max_length=10, verbose_name="Couleur", blank=True, default="orange"
    )

    subheading = models.TextField(
        verbose_name="Sous-titre", null=True, blank=True, default=""
    )

    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Priorité",
        help_text="Priorité d'affichage. Le plus fort, le plus important.",
    )

    deleted = models.DateTimeField(null=True, blank=True)

    precondition_tags = TaggableManager(
        verbose_name="Pré-condition",
        help_text='Affiche ce groupe de questions si TOUS les signaux saisis sont émis </br> Liste de tags séparés par une virgule. Si le tag contient plusieurs mots les encadrer par des guillemets.Attention, veillez à ne pas retirer un tag utilisé dans un projet, celui-ci ne pourra plus être retiré depuis le CRM. ex: "signature convention", diagnostic, "lancement travaux"',
        blank=True,
    )

    def check_precondition(self, session: "Session"):
        """Return true if the precondition is met"""
        my_tags = set(self.precondition_tags.names())
        return my_tags.issubset(session.signals)

    def following(self, direction: DIRECTION):
        """return the following question set defined by the given order_byi sequence"""
        question_sets = self.survey.question_sets

        order_by = Question.ordering(direction)
        iterator = question_sets.order_by(*order_by).iterator()
        for question_set in iterator:
            if question_set == self:
                try:
                    return next(iterator)
                except StopIteration:
                    return None

        return None

    def extreme_question(self, direction: DIRECTION):
        order_by = Question.ordering(direction)
        return self.questions.all().order_by(*order_by).first()

    _clone_m2o_or_o2m_fields = ["questions"]

    def __str__(self):  # pragma: nocover
        return self.heading


class QuestionManager(models.Manager):
    """Manager for active Questions"""

    def get_queryset(self):
        return super().get_queryset().order_by("-priority").filter(deleted=None)


class Question(CloneMixin, models.Model):
    """A question with mutliple choices"""

    objects = QuestionManager()
    objects_all = models.Manager()

    precondition = TagField(
        verbose_name="Pré-condition",
        help_text="Affiche cette question si TOUS les signaux saisis sont émis",
    )

    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Priorité",
        help_text="Priorité d'affichage. Le plus fort, le plus important.",
    )

    question_set = models.ForeignKey(
        QuestionSet, on_delete=models.CASCADE, related_name="questions"
    )
    text = models.CharField(max_length=255, verbose_name="Texte de la question")

    text_short = models.CharField(
        max_length=32, verbose_name="Texte court de la question", default=""
    )

    def _populate_slug(self) -> str:
        return self.text_short if len(self.text_short) else self.text

    slug = AutoSlugField(
        unique=True,
        populate_from=_populate_slug,
        manager=objects_all,
    )

    how = models.TextField(default="", blank=True, verbose_name="Comment ?")

    @property
    def how_rendered(self):
        """Return content as markdown"""
        return markdownify(self.how)

    why = models.TextField(default="", blank=True, verbose_name="Pourquoi ?")

    @property
    def why_rendered(self):
        """Return content as markdown"""
        return markdownify(self.why)

    # does this question expect a multiple choice or single choice answer
    is_multiple = models.BooleanField(
        default=False, blank=True, verbose_name="Est un QCM ?"
    )

    deleted = models.DateTimeField(null=True)

    upload_title = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name="Titre du Téléversement",
        help_text="Si rempli, il sera possible de téléverser un fichier",
    )

    comment_title = models.CharField(
        max_length=255,
        default="Commentaire",
        blank=True,
        verbose_name="Titre du commentaire",
    )

    @staticmethod
    def ordering(direction: DIRECTION):
        return (
            ["-priority", "id"]
            if direction == DIRECTION.NEXT
            else ["priority", "-id"]
            if direction == DIRECTION.PREVIOUS
            else []
        )

    def following(self, direction: DIRECTION):
        """return the following question defined by the given order_by"""
        questions = self.question_set.questions

        order_by = self.ordering(direction)
        iterator = questions.order_by(*order_by).iterator()
        for question in iterator:
            if question == self:
                try:
                    return next(iterator)
                except StopIteration:
                    return None

        return None

    def check_precondition(self, session: "Session"):
        """Return true if the precondition is met"""
        my_tags = set(self.precondition_tags.values_list("name", flat=True))
        return my_tags.issubset(session.signals)

    _clone_m2o_or_o2m_fields = ["choices"]

    def __str__(self):  # pragma: nocover
        return self.text


tagging_register(
    Question,
    tag_descriptor_attr="precondition_tags",
    tagged_item_manager_attr="precondition_tagged",
)


class ChoiceManager(models.Manager):
    """Manager for active Choices"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None).order_by("-priority")


class Choice(CloneMixin, models.Model):
    """A choice for a given Question"""

    objects = ChoiceManager()
    objects_deleted = models.Manager()

    class Meta:
        unique_together = [["value", "question"]]

    value = models.CharField(max_length=30)
    signals = TagField(verbose_name="Signaux")
    text = models.CharField(max_length=255)

    conclusion = models.CharField(max_length=100, blank=True, null=True)

    priority = models.PositiveIntegerField(
        default=0,
        verbose_name="Priorité",
        help_text="Priorité d'affichage. Le plus fort, le plus important.",
        blank=True,
    )

    deleted = models.DateTimeField(null=True)

    question = models.ForeignKey(
        Question, related_name="choices", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.value} / {self.text}"


tagging_register(Choice, tag_descriptor_attr="tags")


class Session(models.Model):
    """A pausable user session with checkpoint for resuming"""

    class Meta:
        unique_together = ("survey", "project")

    survey = models.ForeignKey(
        Survey, related_name="sessions", on_delete=models.CASCADE
    )

    project = models.ForeignKey(
        projects_models.Project, related_name="survey_session", on_delete=models.CASCADE
    )

    @cached_property
    def signals(self):
        """Return the union of signals from Answers of this Session"""
        return {
            tag.name
            for tag in Tag.objects.usage_for_queryset(
                Answer.objects.filter(session=self.pk)
            )
        }

    def _following_question_set(self, direction: DIRECTION, qs=None):
        initial_qs = (
            qs.following(direction)
            if qs
            else self.survey.question_sets.extreme_question(direction)
        )
        qs = initial_qs

        while qs:
            if qs.check_precondition(self):
                return qs
            qs = qs.following(direction)
        return None

    def _following_question(self, direction: DIRECTION, question=None):
        """Return the next unanswered question or None.

        It will trigger only the questions that passes their precondition.
        This is the preferred interface to navigate questions
        """
        answered_questions = Answer.objects.filter(session=self).values_list(
            "question__id", flat=True
        )

        last_not_none_question = question or self.extreme_question(direction)
        if last_not_none_question is None:
            return None

        if not question:
            question = self.extreme_question(direction)
            last_not_none_question = question
        else:
            question = question.following(direction)

        if not question:
            qs = self._following_question_set(
                direction, qs=last_not_none_question.question_set
            )
            question = qs.extreme_question(direction) if qs else None

        while question:
            if question.id not in answered_questions and question.check_precondition(
                self
            ):
                return question
            question = question.following(direction)
            if question is None:
                # No next question in current question set, ask sibling
                qs = self._following_question_set(
                    direction, qs=last_not_none_question.question_set
                )
                question = qs.extreme_question(direction) if qs else None
            else:
                last_not_none_question = question
        return None

    def next_question(self, question=None):
        return self._following_question(DIRECTION.NEXT, question)

    def previous_question(self, question=None):
        return self._following_question(DIRECTION.PREVIOUS, question)

    def extreme_question(self, direction: DIRECTION):
        """Return the first Question of the first Question Set"""
        order_by = Question.ordering(direction)

        for qs in self.survey.question_sets.all():
            for question in qs.questions.all().order_by(*order_by):
                return question

        return None

    def __str__(self):  # pragma: nocover
        return f"Session #{self.id}"

    @property
    def completion(self):
        completions = []
        for qs in self.survey.question_sets.all():
            completions.append(compute_qs_completion(self, qs))

        if not completions:
            return 0

        return math.ceil(statistics.mean(completions))

    @property
    def the_answers(self):
        return self.answers.order_by("question__question_set__id", "question__id")


def empty_answer():
    """Return the empty answer for json values field"""
    return list()


def survey_private_file_path(instance, filename):
    return "survey/session/{0}/{1}".format(instance.session.id, filename)


class Answer(models.Model):
    """Actual answer to a question"""

    class Meta:
        unique_together = (("session", "question"),)

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )

    @property
    def updated_recently(self):
        if self.updated_on:
            return (timezone.now() - self.updated_on) < timedelta(days=4)

        return False

    updated_by = models.ForeignKey(
        auth_models.User,
        on_delete=models.SET_NULL,
        related_name="survey_answers",
        blank=True,
        null=True,
    )

    session = models.ForeignKey(
        Session, related_name="answers", on_delete=models.CASCADE
    )
    question = models.ForeignKey(
        Question, related_name="answers", on_delete=models.CASCADE
    )
    choices = models.ManyToManyField(Choice, related_name="answers")
    value = models.CharField(max_length=30)  # field to be  removed in future version
    values = models.JSONField(default=empty_answer, blank=True)
    signals = TagField(verbose_name="Signaux", blank=True, null=True)
    comment = models.TextField(blank=True)
    attachment = models.FileField(
        blank=True, null=True, upload_to=survey_private_file_path
    )

    @property
    def formatted_value(self) -> str:
        if not self.choices.exists():
            return self.comment
        return ",".join(
            [choice.text for choice in self.choices.all() if len(choice.text)]
        )


tagging_register(Answer, tag_descriptor_attr="tags")
