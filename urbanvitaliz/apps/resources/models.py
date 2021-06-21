# encoding: utf-8

"""
Models for resources application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 10:57:13 CEST
"""

from markdownx.utils import markdownify

from django.db import models

from django.utils import timezone


class Resource(models.Model):
    """Représente une ressource pour les utilisateur·ices d'UV"""

    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    title = models.CharField(max_length=128)
    content = models.TextField()

    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

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
