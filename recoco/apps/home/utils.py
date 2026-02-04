# encoding: utf-8

"""
Utilities for home application

authors: raphael@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-08 09:56:53 CEST
"""

import os
from typing import Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from guardian.shortcuts import assign_perm

from recoco.apps.survey import models as survey_models
from recoco.utils import assign_site_staff, get_group_for_site

from . import models


def get_current_site_sender():
    """Returns the identity for current site email sender"""
    current_site = Site.objects.get_current()
    try:
        site_config = current_site.configuration
    except models.SiteConfiguration.DoesNotExist:
        return settings.DEFAULT_FROM_EMAIL

    return f"{site_config.sender_name} <{site_config.sender_email}>"


def get_current_site_sender_email():
    """Returns the current site email sender"""
    current_site = Site.objects.get_current()
    try:
        site_config = current_site.configuration
    except models.SiteConfiguration.DoesNotExist:
        return settings.DEFAULT_FROM_EMAIL

    return f"{site_config.sender_email}"


def make_new_site(
    name: str,
    domain: str,
    sender_email: str,
    sender_name: str,
    contact_form_recipient: str,
    legal_address: str,
    admin_user: Optional[User] = None,
    email_logo: Optional[str] = "",
) -> Site:
    """Return a new site with given name/domain or None if exists"""
    if Site.objects.filter(domain=domain).count():
        raise Exception(f"The domain {domain} already used")

    with transaction.atomic():
        site = Site.objects.create(name=name, domain=domain)

        survey, created = survey_models.Survey.objects.get_or_create(
            site=site,
            defaults={
                "name": f"Questionnaire par défaut de {name}",
            },
        )

        if created:
            # if we just created the survey, create initial sample questions
            question_set = survey_models.QuestionSet.objects.create(
                survey=survey, heading=f"Thématique d'exemple de '{name}'"
            )
            survey_models.Question.objects.create(
                question_set=question_set,
                text=f"Ceci est une question exemple de '{name}'",
            )

        site_config = models.SiteConfiguration.objects.create(
            site=site,
            project_survey=survey,
            sender_email=sender_email,
            sender_name=sender_name,
            contact_form_recipient=contact_form_recipient,
            legal_address=legal_address,
        )

        if email_logo:
            with open(email_logo, "rb") as email_logo_file:
                dj_file = File(email_logo_file)
                filename = os.path.basename(email_logo)
                site_config.email_logo.save(f"{name}_{filename}", dj_file, save=True)

        with settings.SITE_ID.override(site.pk):
            for group_name, permissions in models.SITE_GROUP_PERMISSIONS.items():
                group = get_group_for_site(group_name, site, create=True)
                for perm_name in permissions:
                    assign_perm(perm_name, group, obj=site)

            if admin_user:
                assign_site_staff(site, admin_user)

        return site

    return None


# rgpd users auto deletion


def deactivate_user(user: User):
    user.is_active = False
    user.save()
    profile = user.profile
    profile.deleted = timezone.now()
    profile.save()


def reactivate_user(crm_user: User):
    crm_user.is_active = True
    crm_user.save()
    profile = crm_user.profile
    profile.deleted = None
    profile.save()


# eof
