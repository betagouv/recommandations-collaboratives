# encoding: utf-8

"""
Models for resources application

authors: raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-16 10:57:13 CEST
"""
import datetime

from django.contrib.auth import models as auth
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.functions import Lower
from django.shortcuts import reverse
from django.utils import timezone
from markdownx.utils import markdownify
from taggit.managers import TaggableManager
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics_models
from watson import search as watson


class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class CategoryOnSiteManager(CurrentSiteManager, CategoryManager):
    pass


class DeletedCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class DeletedCategoryOnSiteManager(CurrentSiteManager, DeletedCategoryManager):
    pass


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

    objects = CategoryManager()
    deleted_objects = DeletedCategoryManager()

    on_site = CategoryOnSiteManager()
    deleted_on_site = DeletedCategoryOnSiteManager()

    sites = models.ManyToManyField(Site)

    name = models.CharField(max_length=128)
    color = models.CharField(max_length=16, choices=COLOR_CHOICES)
    icon = models.CharField(max_length=32)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "catégorie"
        verbose_name_plural = "catégories"

    def __str__(self):  # pragma: nocover
        return self.name

    @property
    def form_label(self):
        return f"cat{self.id}"

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)


class ResourceQuerySet(models.QuerySet):
    """Specific filters for resources"""

    def limit_area(self, departments):
        """Limit resources that match at least one department"""
        return self.filter(
            models.Q(departments__in=departments) | models.Q(departments=None)
        ).distinct()


class ResourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted=None).order_by(Lower("title"))


ResourceManagerWithQS = ResourceManager.from_queryset(ResourceQuerySet)


class ResourceOnSiteManager(CurrentSiteManager, ResourceManagerWithQS):
    pass


class Resource(models.Model):
    """Représente une ressource pour les utilisateur·ices d'UV"""

    DRAFT = 0
    TO_REVIEW = 1
    PUBLISHED = 2

    STATUS_CHOICES = (
        (DRAFT, "Brouillon"),
        (TO_REVIEW, "A relire"),
        (PUBLISHED, "Publié"),
    )

    objects = ResourceManagerWithQS()
    on_site = ResourceOnSiteManager()

    sites = models.ManyToManyField(Site)

    status = models.IntegerField(
        choices=STATUS_CHOICES, verbose_name="État", default=DRAFT
    )

    @property
    def public(self):
        return self.status >= self.TO_REVIEW

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="dernière modification"
    )
    expires_on = models.DateField(
        blank=True, null=True, verbose_name="date d'expiration"
    )
    created_by = models.ForeignKey(
        auth.User,
        on_delete=models.CASCADE,
        related_name="authored_resources",
        null=True,
    )

    def get_absolute_url(self):
        return reverse("resources-resource-detail", kwargs={"resource_id": self.pk})

    def get_embeded_url(self):
        return reverse(
            "resources-resource-detail-embeded", kwargs={"resource_id": self.pk}
        )

    @property
    def expired(self):
        if self.expires_on:
            return self.expires_on < datetime.date.today()
        else:
            return False

    tags = TaggableManager(blank=True)

    category = models.ForeignKey(
        "Category", null=True, blank=True, on_delete=models.CASCADE
    )

    title = models.CharField(max_length=256)
    subtitle = models.CharField(max_length=512, default="", blank=True)
    summary = models.CharField(max_length=512, default="", blank=True)
    content = models.TextField()

    contacts = models.ManyToManyField(
        addressbook_models.Contact, blank=True, verbose_name="Contacts associés"
    )

    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        verbose_name="Départements concernés",
    )

    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ressource"
        verbose_name_plural = "ressources"

    def __str__(self):  # pragma: nocover
        return self.title

    @classmethod
    def fetch(cls):
        return cls.on_site.all()

    @classmethod
    def search(cls, query="", categories=None):
        # A very basic search strategy to be replaced by postgres full text search
        categories = categories or []
        resources = cls.on_site.all()
        if categories:
            resources = resources.filter(
                models.Q(category__in=categories) | models.Q(category=None)
            )

        return watson.filter(resources, query)


class BookmarkManager(models.Manager):
    """Manager for active bookmarks"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)

    def as_list(self):
        return self.values_list("resource", flat=True)


class BookmarkOnSiteManager(CurrentSiteManager, BookmarkManager):
    pass


class DeletedBookmarkManager(models.Manager):
    """Manager for deleted bookmarks"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class DeletedBookmarkOnSiteManager(CurrentSiteManager, DeletedBookmarkManager):
    """Manager for on site deleted bookmarks"""


class Bookmark(models.Model):
    """Represents a bookmark to a resource"""

    objects = BookmarkManager()
    deleted_objects = DeletedBookmarkManager()

    on_site = BookmarkOnSiteManager()
    deleted_on_site = DeletedBookmarkOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    resource = models.ForeignKey("Resource", on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        auth.User, on_delete=models.CASCADE, related_name="bookmarks"
    )

    comments = models.TextField(default="", blank=True)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = []
        verbose_name = "bookmark"
        verbose_name_plural = "bookmarks"

    def __str__(self):  # pragma: nocover
        return f"{self.resource.title}"


# eof
