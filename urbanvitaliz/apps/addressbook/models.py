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
    phone_no = models.CharField(blank=True, max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Courriel")
    division = models.CharField(verbose_name="Service", max_length=100, blank=True)
    organization = models.ForeignKey(
        Organization, related_name="contacts", on_delete=models.CASCADE
    )
