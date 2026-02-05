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
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.files import File
from django.db import transaction
from django.utils import timezone
from guardian.shortcuts import assign_perm

from recoco.apps.communication import constants as communication_constants
from recoco.apps.communication.api import send_email
from recoco.apps.survey import models as survey_models
from recoco.utils import assign_site_staff, get_group_for_site

from ..communication.digests import normalize_user_name
from ..crm.models import Note
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

FIRST_WARNING_DAYS_BEFORE = 30
SECOND_WARNING_DAYS_BEFORE = 7
DELETION_ABSENT_FOR_DAYS = 365 * 2


def delete_user(user: User):
    user.first_name = ""
    user.last_name = "Compte supprimé"
    user.email = f"{user.id}@deleted.recoconseil.fr"
    user.username = user.email
    user.is_active = False
    user.is_superuser = False  # just in case
    user.last_login = None
    user.save()
    user.set_unusable_password()

    user.profile.phone_no = ""
    user.profile.previous_activity_at = None
    user.profile.previous_deletion_warning = None
    user.profile.previous_activity_site = None
    user.profile.nb_deletion_warning = 0
    user.profile.deleted = timezone.now()
    user.profile.save()

    user_content_type = ContentType.objects.get_for_model(User)
    Note.objects.filter(
        content_type_id=user_content_type.id, object_id=user.id
    ).delete()


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


def send_deletion_warning_to_profiles(profiles, warning_time):
    template = (
        communication_constants.TPL_RGDP_DELETION_FIRST_WARNING
        if warning_time == 1
        else communication_constants.TPL_RGDP_DELETION_SECOND_WARNING
    )
    users_by_site = {}
    for profile in profiles:
        users_by_site[profile.previous_activity_site.pk] = (
            [profile.user]
            if profile.previous_activity_site.pk not in users_by_site.keys()
            else users_by_site[profile.previous_activity_site.pk] + [profile.users]
        )
    for site_id, users in users_by_site.items():
        send_deletion_warning_by_site(users, template, site_id)


def send_deletion_warning_by_site(users, template, site_id):
    with settings.SITE_ID.override(site_id):
        send_email(
            template_name=template,
            recipients=[
                {
                    "name": normalize_user_name(user),
                    "email": user.email,
                }
                for user in users
            ],
            params={
                #     site_name, legal_owner, legal_address, site_logo, dashboard_url
            },
        )


# eof
