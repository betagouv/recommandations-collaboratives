# encoding: utf-8

"""
Views for addressbook application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-20 15:56:20 CEST
"""
from django.db import models
from django.db.models.functions import Lower
from urbanvitaliz.apps.geomatics import models as geomatics_models


class OrganizationManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("name"))


class Organization(models.Model):
    objects = OrganizationManager()

    name = models.CharField(max_length=90, verbose_name="Nom")
    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        verbose_name="Départements concernés",
    )

    def __str__(self):  # pragma: nocover
        return "{0}".format(self.name)


class ContactManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by(Lower("last_name"), Lower("first_name"))


class Contact(models.Model):
    objects = ContactManager()

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
