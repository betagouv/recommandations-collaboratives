# encoding: utf-8

"""
Utilities for home application

authors: raphael@beta.gouv.fr, guillaume.libersat@beta.gouv.fr
created: 2021-06-08 09:56:53 CEST
"""

from django.conf import settings
from django.contrib.auth import models as auth_models
from django.contrib.sites.models import Site
from urbanvitaliz.apps.onboarding import models as onboarding_models
from urbanvitaliz.apps.survey import models as survey_models

from urbanvitaliz.utils import make_group_name_for_site

from . import models


def get_current_site_sender():
    """Returns the identity for current site email sender"""
    current_site = Site.objects.get_current()
    try:
        site_config = current_site.configuration
    except models.SiteConfiguration.DoesNotExist:
        return settings.DEFAULT_FROM_EMAIL

    return f"{site_config.sender_name} <{site_config.sender_email}>"


def make_new_site(name: str, domain: str, sender_email: str, sender_name: str) -> Site:
    """Return a new site with given name/domain or None if exists"""
    if Site.objects.filter(domain=domain).count():
        return

    site, created = Site.objects.get_or_create(domain=domain, defaults={"name": name})

    try:
        models.SiteConfiguration.objects.get(site=site)
    except models.SiteConfiguration.DoesNotExist:
        json_form = (
            '[{"type":"header","subtype":"h1","label":"Header"},{"type":"text","required":false,"label":"<br>",'
            '"className":"form-control","name":"text-1660055681026-0","subtype":"text"}]'
        )
        onboarding = onboarding_models.Onboarding.objects.create(json_form)

        survey, created = survey_models.Survey.objects.get_or_create(
            site=site,
            defaults={
                "name": f"Questionnaire par défaut de {name}",
            },
        )

        if created:
            # if we just created the survey, create initial sample questions
            question_set = survey_models.QuestionSet.objects.create(
                survey=survey, heading="Thématique d'exemple"
            )
            survey_models.Question.objects.create(
                question_set=question_set, text="Ceci est une question exemple"
            )

        models.SiteConfiguration.objects.create(
            site=site,
            project_survey=survey,
            onboarding=onboarding,
            sender_email=sender_email,
            sender_name=sender_name,
        )

    for name, permissions in models.SITE_GROUP_PERMISSIONS.items():
        group_name = make_group_name_for_site(name, site)
        auth_models.Group.objects.create(name=group_name)
        # TODO add permission for group

    return site


# eof
