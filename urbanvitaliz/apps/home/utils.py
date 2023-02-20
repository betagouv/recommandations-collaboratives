# encoding: utf-8

"""
Utilities for home application

authors: raphael@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-08 09:56:53 CEST
"""

from django.db import transaction
from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.apps.survey import models as survey_models

from . import models


def get_current_site_sender():
    """Returns the identity for current site email sender"""
    current_site = Site.objects.get_current()
    try:
        site_config = current_site.configuration
    except models.SiteConfiguration.DoesNotExist:
        return settings.DEFAULT_FROM_EMAIL

    return f"{site_config.sender_name} <{site_config.sender_email}>"


def make_group_name_for_site(name: str, site: Site) -> str:
    """Make a group label usable by django for the given site"""
    prefix = site.domain.translate(str.maketrans("-.", "__")).lower()
    return f"{prefix}_{name}"


def make_new_site(name: str, domain: str, sender_email: str, sender_name: str) -> Site:
    """Return a new site with given name/domain or None if exists"""
    if Site.objects.filter(domain=domain).count():
        return
    site = Site.objects.create(name=name, domain=domain)

    onboarding = onboarding_models.Onboarding.objects.create()

    survey = survey_models.Survey.objects.create(
        site=site,
        name=f"Questionnaire {name}",
    )
    question_set = survey_models.QuestionSet.objects.create(
        survey=survey, heading="Thématique d'exemple"
    )
    survey_models.Question.objects.create(
        question_set=question_set, text="Ceci est une question exemple"
    )

    models.SiteConfiguration.objects.create(
        site=site,
        sender_email=sender_email,
        sender_name=sender_name,
        onboarding=onboarding,
        project_survey=survey,
    )

    for name, permissions in models.SITE_GROUP_PERMISSIONS.items():
        group_name = make_group_name_for_site(name, site)
        group = auth_models.Group.objects.create(name=group_name)
        # TODO add permission for group

    return site


# eof
