# encoding: utf-8

"""
Views for addressbook application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-20 15:56:20 CEST
"""
from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.functions import Lower
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from urbanvitaliz.apps.geomatics import models as geomatics_models

from . import apps


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


class OrganizationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("name"))


class OrganizationOnSiteManager(CurrentSiteManager, OrganizationManager):
    pass


class Organization(models.Model):
    objects = OrganizationManager()
    on_site = OrganizationOnSiteManager()

    sites = models.ManyToManyField(Site, related_name="organizations")

    name = models.CharField(max_length=90, verbose_name="Nom")
    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        related_name="organizations",
        verbose_name="Départements concernés",
    )

    def __str__(self):  # pragma: nocover
        return "{0}".format(self.name)

    @classmethod
    def get_or_create(cls, name):
        """Return existing organization with casefree name or new one"""
        organization, _ = cls.objects.get_or_create(
            name__iexact=name, defaults={"name": name}
        )
        return organization


class ContactManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("last_name"), Lower("first_name"))


class ContactOnSiteManager(CurrentSiteManager, ContactManager):
    pass


class Contact(models.Model):
    objects = ContactManager()
    on_site = ContactOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=50, blank=True, verbose_name="Prénom")
    last_name = models.CharField(
        max_length=50, blank=True, verbose_name="Nom de famille"
    )

    @property
    def full_name(self):
        return "{0} {1}".format(self.first_name, self.last_name)

    phone_no = models.CharField(blank=True, max_length=20, verbose_name="Téléphone")
    mobile_no = models.CharField(blank=True, max_length=20, verbose_name="GSM")
    email = models.EmailField(blank=True, verbose_name="Courriel")
    division = models.CharField(verbose_name="Fonction", max_length=100, blank=True)
    organization = models.ForeignKey(
        Organization, related_name="contacts", on_delete=models.CASCADE
    )

    def __str__(self):  # pragma: nocover
        return "{0} {1}".format(self.last_name, self.first_name)


# eof
