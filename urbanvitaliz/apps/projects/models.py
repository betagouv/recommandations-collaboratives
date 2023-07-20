# encoding: utf-8

"""
Models for project

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:33:11 CEST
"""

import os
import uuid

from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from guardian.shortcuts import get_objects_for_user
from markdownx.utils import markdownify
from notifications import models as notifications_models
from ordered_model.models import OrderedModel, OrderedModelManager, OrderedModelQuerySet
from tagging.fields import TagField
from tagging.models import TaggedItem
from tagging.registry import register as tagging_register
from taggit.managers import TaggableManager
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.reminders import models as reminders_models
from urbanvitaliz.apps.resources import models as resources

from urbanvitaliz.utils import CastedGenericRelation, check_if_advisor, has_perm

from . import apps
from .utils import generate_ro_key

FEED_LABEL_MAX_LENGTH = 50

COLLABORATOR_DRAFT_PERMISSIONS = (
    "projects.view_public_notes",
    "projects.use_public_notes",
    "projects.view_project",
    "projects.view_tasks",
    "projects.use_surveys",
    "projects.view_surveys",
)

COLLABORATOR_PERMISSIONS = (
    "projects.use_tasks",
    "projects.manage_documents",
    "projects.invite_collaborators",
    "projects.manage_collaborators",
)

ADVISOR_PERMISSIONS = [
    "projects.view_public_notes",
    "projects.use_advisor_note",
    "projects.use_public_notes",
    "projects.use_private_notes",
    "projects.view_project",
    "projects.view_tasks",
    "projects.manage_tasks",
    "projects.use_tasks",
    "projects.invite_advisors",
    "projects.invite_collaborators",
    "projects.manage_collaborators",
    "projects.change_topics",
    "projects.manage_documents",
    "projects.use_surveys",
    "projects.view_surveys",
]

OBSERVER_PERMISSIONS = ADVISOR_PERMISSIONS


# We need the permission to be associated to the site and not to the projects
@receiver(post_migrate)
def create_site_permissions(sender, **kwargs):
    if sender.name != apps.ProjectConfig.name:
        return

    site_ct = ContentType.objects.get(app_label="sites", model="site")

    auth_models.Permission.objects.get_or_create(
        codename="moderate_projects",
        name="Can moderate incoming projects",
        content_type=site_ct,
    )

    auth_models.Permission.objects.get_or_create(
        codename="list_projects",
        name="Can list projects for site",
        content_type=site_ct,
    )

    auth_models.Permission.objects.get_or_create(
        codename="delete_projects",
        name="Can delete projects for site",
        content_type=site_ct,
    )

    auth_models.Permission.objects.get_or_create(
        codename="use_project_tags",
        name="Can use tags on projects",
        content_type=site_ct,
    )


class ProjectManager(models.Manager):
    """Manager for all projects"""

    def in_departments(self, departments):
        """Return only project with commune in department scope (empty=full)"""
        return self._filter_by_departments(self.filter(deleted=None), departments)

    def _filter_by_departments(self, queryset, departments):
        """Return only project with commune in department scope (empty=full)"""
        result = queryset.exclude(commune=None)
        if departments:
            result = result.filter(commune__department__code__in=departments)
        return result

    def for_user(self, user):
        """Return a list of projects visible to the user"""

        site = Site.objects.get_current()

        if has_perm(user, "sites.list_projects", site):
            projects = self.filter(sites=site, deleted=None)
        else:
            projects = self.none()

        # Reduce scope of projects for regional actors to their area
        if check_if_advisor(user):
            actor_departments = user.profile.departments.values_list("code", flat=True)
            projects = self._filter_by_departments(projects, actor_departments)

        # Extend scope of projects to those where you're member or invited advisor
        my_projects = get_objects_for_user(
            user, "projects.view_project", klass=Project
        ).filter(deleted=None, sites=site)

        return (projects | my_projects).distinct()


class ProjectOnSiteManager(CurrentSiteManager, ProjectManager):
    pass


class ActiveProjectManager(ProjectManager):
    """Manager for active projects"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class ActiveProjectOnSiteManager(CurrentSiteManager, ActiveProjectManager):
    pass


class DeletedProjectManager(ProjectManager):
    """Manager for deleted projects"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class DeletedProjectOnSiteManager(CurrentSiteManager, DeletedProjectManager):
    pass


class Project(models.Model):
    """Représente un project de suivi d'une collectivité"""

    PROJECT_STATES = (
        ("DRAFT", "Brouillon"),
        ("TO_PROCESS", "A traiter"),
        ("READY", "En attente"),  # FIXME A renommer en validé ?
        ("IN_PROGRESS", "En cours"),
        ("DONE", "Traité"),
        ("STUCK", "Conseil Interrompu"),
        # ^ replace by:("STANDBY", "En attente"), FIXME
        ("REJECTED", "Rejeté"),
    )

    objects = ActiveProjectManager()
    objects_deleted = DeletedProjectManager()

    on_site = ActiveProjectOnSiteManager()
    deleted_on_site = DeletedProjectOnSiteManager()

    all_on_site = ProjectOnSiteManager()

    sites = models.ManyToManyField(Site)

    notifications_as_target = CastedGenericRelation(
        notifications_models.Notification,
        related_query_name="target_projects",
        content_type_field="target_content_type",
        object_id_field="target_object_id",
    )

    submitted_by = models.ForeignKey(
        auth_models.User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Déposé par",
        related_name="projects_submitted",
    )

    status = models.CharField(max_length=20, choices=PROJECT_STATES, default="DRAFT")

    members = models.ManyToManyField(auth_models.User, through="ProjectMember")

    @property
    def owner(self):
        return self.members.filter(projectmember__is_owner=True).first()

    ro_key = models.CharField(
        max_length=32,
        editable=False,
        verbose_name="Clé d'accès lecture seule",
        default=generate_ro_key,
        unique=True,
    )

    last_name = models.CharField(
        max_length=128, default="", verbose_name="Nom du contact"
    )
    first_name = models.CharField(
        max_length=128, default="", verbose_name="Prénom du contact"
    )

    publish_to_cartofriches = models.BooleanField(
        verbose_name="Publier sur cartofriches", default=False
    )

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    @property
    def has_blocked_action(self):
        # return self.tasks.filter(status=Task.BLOCKED).count() > 0
        # XXX Uncomment me once status is written
        return False

    exclude_stats = models.BooleanField(default=False, blank=True)
    muted = models.BooleanField(
        default=False, blank=True, verbose_name="Ne pas envoyer de notifications"
    )

    org_name = models.CharField(
        max_length=256, blank=True, default="", verbose_name="Nom de votre structure"
    )

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )

    tags = TaggableManager(blank=True)

    name = models.CharField(max_length=128, verbose_name="Nom du projet")
    phone = models.CharField(
        max_length=16, default="", blank=True, verbose_name="Téléphone"
    )
    description = models.TextField(verbose_name="Description", default="", blank=True)

    # Internal advisors note
    advisors_note = models.TextField(
        verbose_name="Note interne", default="", blank=True, null=True
    )

    @property
    def advisors_note_rendered(self):
        """Return synopsis as markdown"""
        return markdownify(self.advisors_note)

    advisors_note_on = models.DateTimeField(
        verbose_name="Rédigé le", null=True, blank=True
    )
    advisors_note_by = models.ForeignKey(
        auth_models.User,
        verbose_name="Rédigé par",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="advisors_notes",
    )

    location = models.CharField(max_length=256, verbose_name="Localisation")
    commune = models.ForeignKey(
        geomatics_models.Commune,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Commune",
    )
    impediments = models.TextField(default="", blank=True, verbose_name="Difficultés")

    @property
    def impediments_rendered(self):
        """Return impediments as markdown"""
        return markdownify(self.impediments)

    switchtenders = models.ManyToManyField(
        auth_models.User,
        related_name="projects_switchtended",
        blank=True,
        through="ProjectSwitchtender",
        verbose_name="Aiguilleu·r·se·s",
    )

    @property
    def resources(self):
        return self.tasks.exclude(resource=None)

    deleted = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("projects-project-detail", kwargs={"project_id": self.pk})

    class Meta:
        verbose_name = "project"
        verbose_name_plural = "projects"
        permissions = (
            # General
            # Builtin: ("view_project", "Can view the project"),
            # Overview and topics
            ("change_topics", "Can change the topics"),
            ("use_advisor_note", "Can change the advisor note"),
            # Notes
            ("use_private_notes", "Can use the private notes (internal)"),
            ("use_public_notes", "Can use the public notes (conversations)"),
            ("view_public_notes", "Can read the public notes (conversations)"),
            ("view_private_notes", "Can read the private notes (internal)"),
            # Surveys
            ("view_surveys", "Can view the survey results"),
            ("use_surveys", "Can use the surveys"),
            # Tasks/Recommandations
            ("view_tasks", "Can view and list tasks"),
            ("view_draft_tasks", "Can view and list draft tasks"),  # XXX Still useful?
            ("use_tasks", "Can use tasks"),
            ("manage_tasks", "Can manage tasks"),
            # Documents
            ("manage_documents", "Can manage the documents"),
            # Invitation/sharing/members
            ("invite_collaborators", "Can invite collaborators"),
            ("invite_advisors", "Can invite advisors"),
            ("manage_collaborators", "Can manage collaborators"),
            ("manage_advisors", "Can manage advisors"),
        )

    def __str__(self):  # pragma: nocover
        if not self.commune:
            return f"{self.name} - {self.location}"
        return f"{self.commune.name} - {self.name}"


class ProjectMember(models.Model):
    class Meta:
        unique_together = ("member", "project")

    member = models.ForeignKey(auth_models.User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_owner = models.BooleanField(default=False)


class UserProjectStatusOnSiteManager(CurrentSiteManager):
    use_for_related_fields = True


class UserProjectStatus(models.Model):
    """Project status for a given user"""

    # XXX would be better named on_site
    objects = UserProjectStatusOnSiteManager()

    USERPROJECT_STATES = (
        ("NEW", "Nouveau"),
        ("TODO", "A traiter"),
        ("WIP", "En cours"),
        ("DONE", "Traité"),
        ("NOT_INTERESTED", "Pas d'intérêt"),
    )

    class Meta:
        unique_together = ("site", "user", "project")

    # FIXME Ajouter "updated_on"

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="project_states"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="user_project_states"
    )
    status = models.CharField(max_length=20, choices=USERPROJECT_STATES)


class ProjectSwitchtenderOnSiteManager(CurrentSiteManager):
    use_for_related_fields = True


class ProjectSwitchtender(models.Model):
    objects = ProjectSwitchtenderOnSiteManager()

    class Meta:
        unique_together = ("site", "project", "switchtender")

    switchtender = models.ForeignKey(
        auth_models.User,
        on_delete=models.CASCADE,
        related_name="projects_switchtended_on_site",
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="switchtenders_on_site"
    )
    is_observer = models.BooleanField(default=False)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)


class ProjectTopicOnSiteManager(CurrentSiteManager):
    pass


class ProjectTopic(models.Model):
    objects = ProjectTopicOnSiteManager()

    label = models.CharField(max_length=255)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="topics_on_site"
    )
    site = models.ForeignKey(Site, on_delete=models.CASCADE)


class NoteManager(models.Manager):
    """Manager for active tasks"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("-created_on", "-updated_on")
            .filter(deleted=None)
        )

    def public(self):
        return self.get_queryset().filter(public=True)

    def private(self):
        return self.get_queryset().filter(public=False)


class NoteOnSiteManager(CurrentSiteManager, NoteManager):
    pass


class Note(models.Model):
    """Représente un suivi de project"""

    objects = NoteManager()
    on_site = NoteOnSiteManager()

    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, related_name="ptroject_notes"
    )

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="notes"
    )

    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    created_by = models.ForeignKey(
        auth_models.User,
        on_delete=models.SET_NULL,
        related_name="notes_created",
        null=True,
        blank=True,
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    notifications_as_action = CastedGenericRelation(
        notifications_models.Notification,
        related_query_name="action_notes",
        content_type_field="action_object_content_type",
        object_id_field="action_object_object_id",
    )

    document = GenericRelation("Document")

    def get_absolute_url(self):
        if self.public:
            return reverse(
                "projects-project-detail-conversations", args=[self.project.id]
            )
        else:
            return reverse(
                "projects-project-detail-internal-followup", args=[self.project.id]
            )

    def tags_as_list(self):
        """
        Needed since django doesn't provide a split template tag
        """
        tags = []

        words = self.tags.split(" ")
        for word in words:
            tag = word.strip(" ")
            if tag != "":
                tags.append(tag)

        return tags

    content = models.TextField(default="")

    @property
    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "note"
        verbose_name_plural = "notes"

    def __str__(self):  # pragma: nocover
        return f"Note: #{self.id}"


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
    """Représente une action pour faire avancer un project"""

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

    STATUS_CHOICES = (
        (PROPOSED, "proposé"),
        (INPROGRESS, "en cours"),
        (BLOCKED, "blocage"),
        (DONE, "terminé"),
        (NOT_INTERESTED, "pas intéressé·e"),
        (ALREADY_DONE, "déjà fait"),
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    @property
    def closed(self):
        return self.status in [Task.DONE, Task.NOT_INTERESTED, Task.ALREADY_DONE]

    @property
    def open(self):
        return self.status in [Task.PROPOSED, Task.INPROGRESS, Task.BLOCKED]

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="tasks"
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
        default=timezone.now, verbose_name="date de création"
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
        resources.Resource, on_delete=models.CASCADE, null=True, blank=True
    )

    document = GenericRelation("Document")

    contact = models.ForeignKey(
        addressbook_models.Contact, on_delete=models.CASCADE, null=True, blank=True
    )

    #     @property
    #     def is_deadline_past_due(self):
    #         return date.today() > self.deadline if self.deadline else False

    visited = models.BooleanField(default=False, blank=True)

    refused = models.BooleanField(default=False, blank=True)
    done = models.BooleanField(default=False, blank=True)

    status = models.IntegerField(choices=STATUS_CHOICES, default=PROPOSED)

    deleted = models.DateTimeField(null=True, blank=True)

    reminders = GenericRelation(reminders_models.Reminder, related_query_name="tasks")

    class Meta:
        ordering = []
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

    task = models.ForeignKey("Task", on_delete=models.CASCADE, related_name="followups")
    who = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="task_followups"
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

    def trigged_by(self):
        from urbanvitaliz.apps.survey import models as survey_models

        triggers = {}
        for tag in self.condition_tags:
            triggers[tag] = TaggedItem.objects.get_by_model(survey_models.Choice, tag)

        return triggers

    def __str__(self):
        return f"{self.resource.title} - {self.text}"


tagging_register(TaskRecommendation, tag_descriptor_attr="condition_tags")


class DocumentManager(models.Manager):
    """Manager for active document"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class DocumentOnSiteManager(CurrentSiteManager, DocumentManager):
    pass


class DeletedDocumentManager(models.Manager):
    """Manager for deleted documents"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class Document(models.Model):
    """Représente un document associé à un project"""

    objects = DocumentManager()
    on_site = DocumentOnSiteManager()
    objects_deleted = DeletedDocumentManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="documents"
    )

    pinned = models.BooleanField(default=False)

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    uploaded_by = models.ForeignKey(
        auth_models.User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, blank=True, null=True
    )
    object_id = models.PositiveIntegerField(blank=True, null=True)
    attached_object = GenericForeignKey("content_type", "object_id")

    description = models.CharField(max_length=256, default="", blank=True)

    def upload_path(self, filename):
        return "projects/%d/%s" % (self.project.pk, filename)

    the_file = models.FileField(null=True, blank=True, upload_to=upload_path)
    the_link = models.URLField(max_length=500, null=True, blank=True)

    def filename(self):
        return os.path.basename(self.the_file.name)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~Q(Q(the_file__exact="") & Q(the_link__isnull=True)),
                name="not_both_link_and_file_are_null",
            )
        ]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

        verbose_name = "document"
        verbose_name_plural = "documents"

    def __str__(self):  # pragma: nocover
        return f"Document {self.id}"


########################################################################
# helpers / utils
########################################################################


def truncate_string(s, max_length):
    """Truncate given string to max_length"""
    if len(s) < max_length:
        return s
    sub = s[:max_length]
    if s[max_length] != " ":
        # we are truncating last word, rewind to its begining
        sub = sub[:sub.rfind(" ")]
    return f"{sub}…"


# eof
