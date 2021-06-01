# encoding: utf-8

"""
Models for project

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 13:33:11 CEST
"""


from django.db import models

from django.contrib.auth import models as auth

from django.utils import timezone


class Project(models.Model):
    """Représente un project de suivi d'une collectivité"""

    email = models.CharField(max_length=128)
    last_name = models.CharField(
        max_length=128, default="", verbose_name="Nom du contact"
    )
    first_name = models.CharField(
        max_length=128, default="", verbose_name="Prénom du contact"
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
    def fetch(cls):
        return cls.objects.filter(deleted=None)

    def notes(self):
        return Note.fetch().filter(project=self).order_by("created_on")

    def tasks(self):
        return Task.fetch().filter(project=self).order_by("created_on")


class Note(models.Model):
    """Représente un suivi de project"""

    project = models.ForeignKey("Project", on_delete=models.CASCADE)
    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    content = models.TextField(default="")

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
    tags = models.CharField(max_length=256, blank=True, default="")

    content = models.TextField(default="")
    deadline = models.DateField(null=True, blank=True)
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


class Resource(models.Model):
    """Représente une ressource du système"""

    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    title = models.CharField(max_length=128)
    content = models.TextField()

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "ressource"
        verbose_name_plural = "ressources"

    def __str__(self):
        return "Resource".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


# eof
