# encoding: utf-8

"""
Models for project

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:33:11 CEST
"""
import uuid
from datetime import date

from django.contrib.auth import models as auth_models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from markdownx.utils import markdownify
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from urbanvitaliz.apps.resources import models as resources


class Project(models.Model):
    """Représente un project de suivi d'une collectivité"""

    email = models.CharField(max_length=128)
    emails = models.JSONField(default=list)  # list of person having access to project

    ro_key = models.CharField(
        max_length=32,
        editable=False,
        verbose_name="Clé d'accès lecture seule",
        default=lambda: uuid.uuid4().hex,
    )

    last_name = models.CharField(
        max_length=128, default="", verbose_name="Nom du contact"
    )
    first_name = models.CharField(
        max_length=128, default="", verbose_name="Prénom du contact"
    )

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    is_draft = models.BooleanField(default=True, blank=True)

    org_name = models.CharField(
        max_length=256, blank=True, default="", verbose_name="Nom de votre structure"
    )

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    name = models.CharField(max_length=128, verbose_name="Nom du projet")
    phone = models.CharField(
        max_length=16, default="", blank=True, verbose_name="Téléphone"
    )
    description = models.TextField(verbose_name="Description")
    location = models.CharField(max_length=256, verbose_name="Localisation")
    commune = models.ForeignKey(
        geomatics_models.Commune,
        null=True,
        on_delete=models.CASCADE,
        verbose_name="Commune",
    )
    impediments = models.TextField(default="", blank=True, verbose_name="Difficultés")

    @property
    def resources(self):
        return self.tasks.exclude(resource=None)

    deleted = models.DateTimeField(null=True, blank=True)

    def get_absolute_url(self):
        return reverse("projects-project-detail", kwargs={"project_id": self.pk})

    class Meta:
        ordering = []
        verbose_name = "project"
        verbose_name_plural = "projects"

    def __str__(self):
        return f"{self.name} {self.location}"

    @classmethod
    def fetch(cls, email=None):
        projects = cls.objects.filter(deleted=None)
        if email:
            projects = projects.filter(emails__contains=email)
        return projects

    def notes(self):
        return Note.fetch().filter(project=self).order_by("created_on")

    def tasks(self):
        return Task.fetch().filter(project=self).order_by("deadline", "created_on")


class NoteManager(models.Manager):
    """Manager for active tasks"""

    def public(self):
        return self.filter(public=True)

    def private(self):
        return self.filter(public=False)


class Note(models.Model):
    """Représente un suivi de project"""

    objects = NoteManager()

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="notes"
    )
    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

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

    def __str__(self):
        return "Note".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


class TaskManager(models.Manager):
    """Manager for active tasks"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("-priority", "-updated_on")
            .filter(deleted=None)
        )

    def accepted(self):
        return self.filter(accepted=True, refused=False)

    def proposed(self):
        return self.filter(accepted=False, refused=False)

    def refused(self):
        return self.filter(refused=True)

    def done(self):
        return self.filter(accepted=True, done=True, refused=False)

    def open(self):
        return self.filter(accepted=True, done=False, refused=False)


class DeletedTaskManager(models.Manager):
    """Manager for deleted tasks"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class Task(models.Model):
    """Représente une action pour faire avancer un project"""

    objects = TaskManager()
    deleted_objects = DeletedTaskManager()

    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="tasks"
    )
    public = models.BooleanField(default=False, blank=True)
    priority = models.PositiveIntegerField(
        default=0,
        blank=True,
        verbose_name="Priorité",
        help_text="Plus le chiffre est élevé, plus la recommandation s'affichera en haut.",
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

    intent = models.CharField(
        max_length=256, blank=True, default="", verbose_name="Intention"
    )
    content = models.TextField(default="", verbose_name="Contenu")

    @property
    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

    deadline = models.DateField(null=True, blank=True)

    resource = models.ForeignKey(
        resources.Resource, on_delete=models.CASCADE, null=True, blank=True
    )

    contact = models.ForeignKey(
        addressbook_models.Contact, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def is_deadline_past_due(self):
        return date.today() > self.deadline if self.deadline else False

    accepted = models.BooleanField(default=False, blank=True)
    refused = models.BooleanField(default=False, blank=True)
    done = models.BooleanField(default=False, blank=True)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "action"
        verbose_name_plural = "actions"

    def __str__(self):
        return "Task".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


class Document(models.Model):
    """Représente un document associé à un project"""

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    description = models.CharField(max_length=256, default="", blank=True)
    the_file = models.FileField()

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "document"
        verbose_name_plural = "documents"

    def __str__(self):
        return "Document".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


# eof
