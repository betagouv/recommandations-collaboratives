# encoding: utf-8

"""
Models for resources application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 10:57:13 CEST
"""

from markdownx.utils import markdownify

from django.db import models

from django.utils import timezone


class Category(models.Model):
    """Représente une categorie de ressource"""

    COLOR_CHOICES = (
        ("blue", "Bleu"),
        ("black", "Black"),
        ("yellow", "Jaune"),
        ("orange", "Orange"),
        ("red", "Rouge"),
        ("green", "Vert"),
        ("violet", "Violet"),
    )

    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16, choices=COLOR_CHOICES)
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
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="dernière modification"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    def tags_as_list(self):
        """
        Needed since django doesn't provide a split template tag
        XXX: Temp Duplicated before introducing a Tag manager
        """
        tags = []

        words = self.tags.split(" ")
        for word in words:
            tag = word.strip(" ")
            if tag != "":
                tags.append(tag)

        return tags


    category = models.ForeignKey("Category", null=True, on_delete=models.CASCADE)

    title = models.CharField(max_length=128)
    subtitle = models.CharField(max_length=128, default="")
    quote = models.CharField(max_length=256, default="")
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
