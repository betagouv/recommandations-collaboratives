# encoding: utf-8

"""
Models for resources application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 10:57:13 CEST
"""

from markdownx.utils import markdownify

from django.db import models

from django.utils import timezone

from django.contrib.auth import models as auth

from urbanvitaliz.apps.projects import models as projects


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

    @property
    def form_label(self):
        return f"cat{self.id}"

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

    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.CASCADE
    )

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=512, default="")
    quote = models.CharField(max_length=512, default="")
    content = models.TextField()

    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ressource"
        verbose_name_plural = "ressources"

    def __str__(self):
        return self.title

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)

    @classmethod
    def search(cls, query="", categories=None):
        # A very basic search strategy to be replaced by postgres full text search
        categories = categories or []
        resources = cls.fetch()
        if categories:
            resources = resources.filter(
                models.Q(category__in=categories) | models.Q(category=None)
            )
        for word in query.split():
            resources = resources.filter(
                models.Q(title__icontains=word)
                | models.Q(subtitle__icontains=word)
                | models.Q(content__icontains=word)
                | models.Q(quote__icontains=word)
                | models.Q(tags__icontains=word)
            )
        return resources


class Bookmark(models.Model):
    """Represents a bookmark to a resource"""

    resource = models.ForeignKey("Resource", on_delete=models.CASCADE)
    created_by = models.ForeignKey(auth.User, on_delete=models.CASCADE)

    project = models.ForeignKey(projects.Project, null=True, on_delete=models.CASCADE)
    comments = models.TextField(default="", blank=True)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "bookmark"
        verbose_name_plural = "bookmarks"

    def __str__(self):
        return f"{self.resource.title}"

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


# eof
