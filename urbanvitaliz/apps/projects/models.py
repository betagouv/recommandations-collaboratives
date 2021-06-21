# encoding: utf-8

"""
Models for project

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:33:11 CEST
"""
from datetime import date

from django.db import models

from django.contrib.auth import models as auth

from django.utils import timezone

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Project(models.Model):
    """Représente un project de suivi d'une collectivité"""

    email = models.CharField(max_length=128)
    last_name = models.CharField(
        max_length=128, default="", verbose_name="Nom du contact"
    )
    first_name = models.CharField(
        max_length=128, default="", verbose_name="Prénom du contact"
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
    tags = models.CharField(max_length=256, blank=True, default="")

    name = models.CharField(max_length=128, verbose_name="Nom du projet")
    description = models.TextField(verbose_name="Description")
    location = models.CharField(max_length=256, verbose_name="Localisation")
    impediments = models.TextField(default="", blank=True, verbose_name="Difficultés")

    deleted = models.DateTimeField(null=True, blank=True)

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
            projects = projects.filter(email=email)
        return projects

    def notes(self):
        return Note.fetch().filter(project=self).order_by("created_on")

    def tasks(self):
        return Task.fetch().filter(project=self).order_by("deadline", "created_on")


class Note(models.Model):
    """Représente un suivi de project"""

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
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


class Task(models.Model):
    """Représente une action pour faire avancer un project"""

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    content = models.TextField(default="")
    deadline = models.DateField(null=True, blank=True)

    @property
    def is_deadline_past_due(self):
        return date.today() > self.deadline if self.deadline else False

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
