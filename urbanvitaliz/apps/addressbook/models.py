from django.db import models

from urbanvitaliz.apps.geomatics import models as geomatics_models


class Organization(models.Model):
    name = models.CharField(max_length=90)
    departments = models.ManyToManyField(
        geomatics_models.Department,
        blank=True,
        verbose_name="Départements concernés",
    )


class Contact(models.Model):
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_no = models.CharField(blank=True, max_length=20)
    email = models.EmailField(blank=True)
    division = models.CharField(verbose_name="Service", max_length=100, blank=True)
    organization = models.ForeignKey(
        Organization, related_name="contacts", on_delete=models.CASCADE
    )
