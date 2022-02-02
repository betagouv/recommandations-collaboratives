# encoding: utf-8

"""
Models for communication

author  : raphael.marvie@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created : 2021-12-21 12:40:54 CEST
"""

from django.db import models


class EmailTemplate(models.Model):
    name = models.CharField(max_length=40, unique=True)
    sib_id = models.IntegerField()

    def __str__(self):
        return f"{self.name} - {self.sib_id}"


# eof
