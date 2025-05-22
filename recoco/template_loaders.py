# -*- coding: utf-8 -*-
# Backported from django-multisite
import os

from django.conf import settings
from django.contrib.sites.models import Site
from django.template.loaders.filesystem import Loader as FilesystemLoader


class Loader(FilesystemLoader):
    """
    Overload default templates by Site specific one, found in a directory
    matching the site name.
    """

    default_dir = getattr(settings, "MULTISITE_DEFAULT_TEMPLATE_DIR", "default")

    def get_template_sources(self, *args, **kwargs):
        template_name = args[0]
        domain = Site.objects.get_current().domain

        for tname in (
            os.path.join(domain, template_name),
            os.path.join(self.default_dir, template_name),
        ):
            args = [tname]
            for item in super().get_template_sources(*args, **kwargs):
                yield item
