# encoding: utf-8

"""
Utilities for home application

authors: raphael@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-08 09:56:53 CEST
"""

from django import forms
from django.conf import settings
from django.contrib.auth import models as auth
from django.contrib.sites.models import Site

from . import models


def get_current_site_sender():
    current_site = Site.objects.get_current()
    try:
        site_config = current_site.configuration
    except models.SiteConfiguration.DoesNotExist:
        return settings.DEFAULT_FROM_EMAIL

    return f"{site_config.sender_name} <{site_config.sender_email}>"


# eof
