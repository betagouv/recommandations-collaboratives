# encoding: utf-8

"""
Models for resources application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 10:57:13 CEST
"""

from django.db import models

from django.utils import timezone


class Category(models.Model):
    """Représente une categorie de ressource"""

    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16)
    icon = models.CharField(max_length=32)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):
        return self.name

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


class Resource(models.Model):
    """Représente une ressource pour les utilisateur·ices d'UV"""

    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="dernière modification"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    category = models.ForeignKey("Category", null=True, on_delete=models.CASCADE)

    title = models.CharField(max_length=128)
    content = models.TextField()

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ressource"
        verbose_name_plural = "ressources"

    def __str__(self):
        return "Resource".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)

    @classmethod
    def search(cls, criterias):
        return cls.fetch()


# eof
