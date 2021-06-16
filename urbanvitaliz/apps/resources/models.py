from django.db import models


class Resource(models.Model):
    """Représente une ressource du système"""

    public = models.BooleanField(default=False, blank=True)
    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date de création"
    )
    tags = models.CharField(max_length=256, blank=True, default="")

    title = models.CharField(max_length=128)
    content = models.TextField()

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "ressource"
        verbose_name_plural = "ressources"

    def __str__(self):
        return "Resource".format()

    @classmethod
    def fetch(cls):
        return cls.objects.filter(deleted=None)
