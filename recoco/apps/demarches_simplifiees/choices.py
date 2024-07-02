from django.db import models


class DSType(models.TextChoices):
    DETR_DSIL = "DETR_DSIL", "DETR DSIL"
