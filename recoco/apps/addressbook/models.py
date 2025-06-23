# encoding: utf-8

"""
Views for addressbook application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-20 15:56:20 CEST
"""

import logging

import reversion
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Count
from django.db.models.functions import Lower
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from model_utils.models import TimeStampedModel

from recoco.apps.geomatics import models as geomatics_models

from . import apps

logger = logging.getLogger(__name__)


# We need the permission to be associated to the site and not to the projects
@receiver(post_migrate)
def create_site_permissions(sender, **kwargs):
    if sender.name != apps.AddressbookConfig.name:
        return

    site_ct = ContentType.objects.get(app_label="sites", model="site")

    auth_models.Permission.objects.get_or_create(
        codename="use_addressbook",
        name="Can use the addressbook for site",
        content_type=site_ct,
    )


class OrganizationGroup(TimeStampedModel):
    name = models.CharField(max_length=90, verbose_name="Nom")

    class Meta:
        verbose_name = "Groupement d'organisations"
        verbose_name_plural = "Groupements d'organisations"

    def __str__(self):
        return self.name


class OrganizationQuerySet(models.QuerySet):
    def with_contacts_only(self):
        return self.annotate(contact_count=Count("contacts")).filter(
            contact_count__gt=0
        )


class OrganizationManager(models.Manager.from_queryset(OrganizationQuerySet)):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("name"))


class OrganizationOnSiteManager(CurrentSiteManager, OrganizationManager):
    pass


class Organization(TimeStampedModel):
    objects = OrganizationManager()
    on_site = OrganizationOnSiteManager()

    sites = models.ManyToManyField(Site, related_name="organizations")

    name = models.CharField(
        max_length=90,
        verbose_name="Nom",
        unique=True,
    )

    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        related_name="organizations",
        verbose_name="Départements concernés",
    )

    group = models.ForeignKey(
        OrganizationGroup,
        on_delete=models.CASCADE,
        related_name="organizations",
        blank=True,
        null=True,
    )

    def __str__(self):  # pragma: nocover
        return "{0}".format(self.name)

    @property
    def has_departments(self):
        return self.departments.exists()

    @classmethod
    def get_or_create(cls, name):
        """Return existing organization with casefree name or new one"""
        try:
            organization, _ = cls.objects.get_or_create(
                name__iexact=name, defaults={"name": name}
            )
        except cls.MultipleObjectsReturned:
            organization = (
                cls.objects.filter(name__iexact=name).order_by("-created").first()
            )
            logger.error(
                f"Multiple organizations found with name {name} (case insensitive)"
            )
        return organization


class ContactManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("last_name"), Lower("first_name"))


class ContactOnSiteManager(CurrentSiteManager, ContactManager):
    pass


@reversion.register(
    fields=("first_name", "last_name", "phone_no", "mobile_no", "email", "division")
)
class Contact(TimeStampedModel):
    objects = ContactManager()
    on_site = ContactOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=50, blank=True, verbose_name="Prénom")
    last_name = models.CharField(
        max_length=50, blank=True, verbose_name="Nom de famille"
    )
    phone_no = models.CharField(blank=True, max_length=20, verbose_name="Téléphone")
    mobile_no = models.CharField(blank=True, max_length=20, verbose_name="GSM")
    email = models.EmailField(blank=True, verbose_name="Courriel")
    division = models.CharField(verbose_name="Fonction", max_length=100, blank=True)
    organization = models.ForeignKey(
        Organization, related_name="contacts", on_delete=models.CASCADE
    )

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    def __str__(self):  # pragma: nocover
        return "{0} {1}".format(self.last_name, self.first_name)


# eof
