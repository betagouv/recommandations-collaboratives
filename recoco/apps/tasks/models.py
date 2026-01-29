# encoding: utf-8

"""
Models for project

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:33:11 CEST
"""

import uuid

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from markdownx.utils import markdownify
from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet
from tagging.fields import TagField
from tagging.models import TaggedItem  # remains necessary for survey-related code
from tagging.registry import register as tagging_register
from taggit.managers import TaggableManager

from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.geomatics import models as geomatics_models
from recoco.apps.projects import models as projects_models
from recoco.apps.resources import models as resources

FEED_LABEL_MAX_LENGTH = 50


class TaskQuerySet(OrderedModelQuerySet):
    pass


class TaskManager(OrderedModelManager):
    """Manager for active tasks"""

    def get_queryset(self):
        return (
            TaskQuerySet(self.model, using=self._db)
            .order_by("order", "-updated_on")
            .filter(deleted=None)
        )

    def published(self):
        return self.filter(public=True)

    def unpublished_open(self):
        return self.unpublished_proposed() | self.filter(status=Task.INPROGRESS)

    def open(self):
        return self.proposed() | self.filter(status=Task.INPROGRESS, public=True)

    def unpublished_proposed(self):
        return self.filter(Q(status=Task.PROPOSED) | Q(status=Task.BLOCKED))

    def proposed(self):
        return self.filter(
            Q(status=Task.PROPOSED) | Q(status=Task.BLOCKED), public=True
        )

    def not_interested(self):
        return self.filter(status=Task.NOT_INTERESTED)

    def already_done(self):
        return self.filter(status=Task.ALREADY_DONE)

    def done(self):
        return self.filter(status=Task.DONE)

    def done_or_already_done(self):
        return self.filter(Q(status=Task.DONE) | Q(status=Task.ALREADY_DONE))

    def closed(self):
        return self.filter(
            status__in=(Task.DONE, Task.ALREADY_DONE, Task.NOT_INTERESTED)
        )


class TaskOnSiteManager(CurrentSiteManager, TaskManager):
    pass


class DeletedTaskManager(models.Manager):
    """Manager for deleted tasks"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class DeletedTaskOnSiteManager(CurrentSiteManager, DeletedTaskManager):
    pass


class Task(OrderedModel):
    """Représente une recommandation/action pour faire avancer un project"""

    objects = TaskManager()
    deleted_objects = DeletedTaskManager()

    on_site = TaskOnSiteManager()
    deleted_on_site = DeletedTaskOnSiteManager()

    order_with_respect_to = ("site", "project")

    PROPOSED = 0
    INPROGRESS = 1
    BLOCKED = 2
    DONE = 3
    NOT_INTERESTED = 4
    ALREADY_DONE = 5

    OPEN_STATUSES = [PROPOSED, INPROGRESS, BLOCKED]
    CLOSED_STATUSES = [DONE, NOT_INTERESTED, ALREADY_DONE]

    STATUS_CHOICES = (
        (PROPOSED, "proposé"),
        (INPROGRESS, "en cours"),
        (BLOCKED, "blocage"),
        (DONE, "terminé"),
        (NOT_INTERESTED, "pas intéressé·e"),
        (ALREADY_DONE, "déjà fait"),
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    topic = models.ForeignKey(
        projects_models.Topic,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tasks",
    )

    @property
    def closed(self):
        return self.status in self.CLOSED_STATUSES

    @property
    def open(self):
        return self.status in self.OPEN_STATUSES

    project = models.ForeignKey(
        projects_models.Project, on_delete=models.CASCADE, related_name="tasks"
    )
    public = models.BooleanField(default=False, blank=True)
    priority = models.PositiveIntegerField(
        default=1000,
        blank=True,
        verbose_name="Priorité",
        help_text=(
            "Plus le chiffre est élevé, plus la recommandation s'affichera en haut."
        ),
    )

    created_by = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="tasks_created"
    )

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date et heure de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    #     def tags_as_list(self):
    #         """
    #         Needed since django doesn't provide a split template tag
    #         """
    #         tags = []
    #
    #         words = self.tags.split(" ")
    #         for word in words:
    #             tag = word.strip(" ")
    #             if tag != "":
    #                 tags.append(tag)
    #
    #         return tags

    intent = models.CharField(
        max_length=256, blank=True, default="", verbose_name="Intention"
    )
    content = models.TextField(default="", verbose_name="Contenu", blank=True)

    @property
    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

    deadline = models.DateField(null=True, blank=True)

    resource = models.ForeignKey(
        resources.Resource,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="recommandations",
    )

    document = GenericRelation(projects_models.Document)

    contact = models.ForeignKey(
        addressbook_models.Contact, on_delete=models.SET_NULL, null=True, blank=True
    )

    #     @property
    #     def is_deadline_past_due(self):
    #         return date.today() > self.deadline if self.deadline else False

    visited = models.BooleanField(default=False, blank=True)

    refused = models.BooleanField(default=False, blank=True)
    done = models.BooleanField(default=False, blank=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=PROPOSED)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "action"
        verbose_name_plural = "actions"

    def __str__(self):  # pragma: nocover
        return "Task:{0}".format(self.intent or self.id)

    def feed_label(self, max_length=FEED_LABEL_MAX_LENGTH):
        """Return a truncated version of intent for feeds"""
        label = truncate_string(self.intent, max_length)
        return f"«{label}»"

    def get_absolute_url(self):
        return (
            reverse("projects-project-detail-actions", args=[self.project.id])
            + f"#action-{self.pk}"
        )


class TaskFollowupManager(models.Manager):
    """Manager for followups"""

    def get_queryset(self):
        return super().get_queryset().order_by("timestamp")


class TaskFollowup(models.Model):
    """An followup on the task -- achievements and comments"""

    objects = TaskFollowupManager()

    task = models.ForeignKey(
        "Task",
        on_delete=models.CASCADE,
        related_name="followups",
    )
    who = models.ForeignKey(
        auth_models.User,
        on_delete=models.CASCADE,
        related_name="task_followups",
    )
    contact = models.ForeignKey(
        addressbook_models.Contact,
        on_delete=models.SET_NULL,
        related_name="task_followups",
        null=True,
        blank=True,
    )
    status = models.IntegerField(choices=Task.STATUS_CHOICES, blank=True, null=True)

    @property
    def status_txt(self):
        return {
            Task.PROPOSED: "nouveau",
            Task.INPROGRESS: "en cours",
            Task.BLOCKED: "bloquée",
            Task.DONE: "terminée",
            Task.NOT_INTERESTED: "pas intéressé",
            Task.ALREADY_DONE: "déjà faite",
        }.get(self.status, "?")

    timestamp = models.DateTimeField(default=timezone.now)
    comment = models.TextField(default="", blank=True)

    class Meta:
        verbose_name = "suivi action"
        verbose_name_plural = "suivis actions"

    @property
    def comment_rendered(self):
        """Return comment as markdown"""
        return markdownify(self.comment)

    def __str__(self):  # pragma: nocover
        return f"TaskFollowup{self.id}"

    def feed_label(self):
        """Return a truncated version of task intent for feeds"""
        return self.task.feed_label()

    def get_absolute_url(self):
        task = self.task
        return (
            reverse("projects-project-detail-actions", args=[task.project.id])
            + f"#action-{task.pk}"
        )


class TaskFollowupRsvp(models.Model):
    """Task followup request sent to project owner."""

    uuid = models.UUIDField(default=uuid.uuid4, primary_key=True)
    task = models.ForeignKey(
        "Task", on_delete=models.CASCADE, related_name="rsvp_followups"
    )
    user = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="rsvp_followups"
    )
    created_on = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "rsvp suivi action"
        verbose_name_plural = "rsvp suivis actions"

    def __str__(self):  # pragma: nocover
        return f"TaskFollowupRsvp{self.uuid}"


class TaskRecommendationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("resource__title")


class TaskRecommendationOnSiteManager(CurrentSiteManager, TaskRecommendationManager):
    pass


class TaskRecommendation(models.Model):
    """Recommendation mechanisms for Tasks"""

    objects = TaskRecommendationManager()
    on_site = TaskRecommendationOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    condition = TagField(verbose_name="Condition", blank=True, null=True)
    resource = models.ForeignKey(
        resources.Resource,
        on_delete=models.CASCADE,
        related_name="task_recommendations",
    )
    text = models.TextField()
    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        verbose_name="Départements concernés",
    )
    condition_tags_taggit = TaggableManager(blank=True)

    def trigged_by(self):
        from recoco.apps.survey import models as survey_models

        triggers = {}
        for tag in self.condition_tags_taggit.all():
            triggers[tag] = TaggedItem.objects.get_by_model(
                survey_models.Choice.objects.prefetch_related(
                    "question__question_set"
                ).select_related("question"),
                tag.name,
            )

        return triggers

    def __str__(self):
        return f"{self.resource.title} - {self.text}"


tagging_register(TaskRecommendation, tag_descriptor_attr="condition_tags")


########################################################################
# helpers / utils
########################################################################


def truncate_string(s, max_length):
    """Truncate given string to max_length"""
    if len(s) <= max_length:
        return s
    sub = s[:max_length]
    if s[max_length] != " ":
        # we are truncating last word, rewind to its begining
        sub = sub[: sub.rfind(" ")]
    return f"{sub}…"


# eof
