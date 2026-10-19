from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models


class PluginModel(models.Model):
    """Base class for every concrete model of a plugin (``plugin_*``) app.

    Plugin tables live in one schema per plugin, shared by all tenants, so
    rows are scoped by ``site`` like core models do.

    ``objects`` stays unscoped and comes first so that it is the
    ``_default_manager`` (used by watson, the admin, generic relations).
    Use ``on_site`` in views and anywhere tenant data is exposed.
    """

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    class Meta:
        abstract = True
