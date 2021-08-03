# encoding: utf-8

"""
Views for addressbook application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-07-20 15:56:20 CEST
"""
from django.db import models
from urbanvitaliz.apps.geomatics import models as geomatics_models


class Organization(models.Model):
    name = models.CharField(max_length=90, verbose_name="Nom")
    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        verbose_name="Départements concernés",
    )

    def __str__(self):
        return "Organization: {0}".format(self.name)


class Contact(models.Model):
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
    division = models.CharField(verbose_name="Service", max_length=100, blank=True)
    organization = models.ForeignKey(
        Organization, related_name="contacts", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.full_name


# eof
