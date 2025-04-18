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

    def __str__(self):  # pragma: nocover
        return self.name


class DepartmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("name")


class Department(models.Model):
    """Represents a Department"""

    objects = DepartmentManager()

    region = models.ForeignKey(
        "Region", on_delete=models.CASCADE, related_name="departments"
    )

    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "département"
        verbose_name_plural = "départements"

    def __str__(self):  # pragma: nocover
        return self.name


class Commune(models.Model):
    """Represents a Commune"""

    department = models.ForeignKey("Department", on_delete=models.CASCADE)

    insee = models.CharField(max_length=5)
    postal = models.CharField(max_length=5)
    name = models.CharField(max_length=64)

    longitude = models.FloatField(default=0.0)
    latitude = models.FloatField(default=0.0)

    class Meta:
        verbose_name = "commune"
        verbose_name_plural = "communes"
        unique_together = [["insee", "postal"]]

    def __str__(self):  # pragma: nocover
        return self.name

    @classmethod
    def get_by_postal_code(cls, code):
        """Return first commune matching given postal code or None"""
        try:
            return cls.objects.filter(postal=code)[0]
        except IndexError:
            return

    @classmethod
    def get_by_insee_code(cls, code):
        """Return commune matching the given insee code or None"""
        try:
            return cls.objects.filter(insee=code).first()
        except IndexError:
            return

    @property
    def postal_and_insee_codes(self) -> list[str]:
        return [self.postal, self.insee]


# eof
