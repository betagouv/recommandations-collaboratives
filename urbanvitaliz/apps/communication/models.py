# encoding: utf-8

"""
Models for communication

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-12-21 12:40:54 CEST
"""

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class EmailTemplate(models.Model):
    class Meta:
        unique_together = ("site", "name")

    objects = models.Manager()
    on_site = CurrentSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    name = models.CharField(max_length=40)
    sib_id = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.sib_id}"


# eof
