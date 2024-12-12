from django.contrib.sites.models import Site
from django.db import models
from hitcount.models import HitCountBase


class HitCount(HitCountBase):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    tag = models.CharField(max_length=50, blank=True, null=True)

    class Meta(HitCountBase.Meta):
        db_table = "hitcount_hit_count"
