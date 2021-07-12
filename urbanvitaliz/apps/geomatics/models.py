# encoding: utf-8

"""
Models for application geomatics

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-07-12 12:05:28 CEST
"""


from django.db import models


class Region(models.Model):
    """Represents a Region"""

    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "région"
        verbose_name_plural = "régions"

    def __str__(self):
        return self.name


class Department(models.Model):
    """Represents a Department"""

    region = models.ForeignKey("Region", on_delete=models.CASCADE)

    code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "département"
        verbose_name_plural = "départements"

    def __str__(self):
        return self.name


class Commune(models.Model):
    """Represents a Commune"""

    department = models.ForeignKey("Department", on_delete=models.CASCADE)

    insee = models.CharField(max_length=5)
    postal = models.CharField(max_length=5)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "commune"
        verbose_name_plural = "communes"

    def __str__(self):
        return self.name


# eof
