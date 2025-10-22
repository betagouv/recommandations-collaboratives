# encoding: utf-8

"""
api for sending emails

Always use the send_email function that can be implemented as:

- a debug version through the terminal
- a production version through send in blue


authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
updated: 2022-02-03 16:19:24 CET
"""

import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import mail_admins
from django.core.mail import send_mail as django_send_mail
from django.utils import timezone

from recoco.apps.home.models import SiteConfiguration
from recoco.utils import build_absolute_url

from .brevo import Brevo
from .models import EmailTemplate, TransactionRecord

logger = logging.getLogger("main")


def create_transaction(transaction_id, recipients, label, related, faked=False):
    current_site = Site.objects.get_current()

    if not isinstance(recipients, list):
        recipients = [recipients]

    if isinstance(recipients[0], dict):
        recipients = [recipient.get("email") for recipient in recipients]

    for user in User.objects.filter(profile__sites=current_site, email__in=recipients):
        TransactionRecord.objects.create(
            site=current_site,
            sent_on=timezone.now(),
            transaction_id=transaction_id,
            label=label,
            faked=faked,
            user=user,
            related=related,
        )


def get_site_params():
    params = {}
    current_site = Site.objects.get_current()
    params["site_name"] = current_site.name
    params["site_domain"] = current_site.domain

    site_config = SiteConfiguration.objects.get(site=current_site)
    params["legal_address"] = site_config.legal_address or ""
    params["legal_owner"] = site_config.legal_owner or ""
    params["description"] = site_config.description or ""
    params["sender_email"] = site_config.sender_email or ""

    if site_config.email_logo:
        params["site_logo"] = build_absolute_url(site_config.email_logo.url)

    return params


def brevo_email(template_name, recipients, params=None, test=False, related=None):
    """Uses Brevo service to send an email using the given template and params"""
    brevo = Brevo()
    try:
        # try to use the site specific template
        template = EmailTemplate.on_site.get(name__iexact=template_name)
    except EmailTemplate.DoesNotExist:
        try:
            # use default template
            template = EmailTemplate.objects.get(site=None, name__iexact=template_name)
        except EmailTemplate.DoesNotExist:
            current_site = Site.objects.get_current()
            mail_admins(
                subject="Unable to send email",
                message=f"{template_name} was not found on {current_site} !",
            )
            return False

    # enriches params with site data
    all_params = get_site_params()
    if params:
        all_params.update(params)

    response = brevo.send_email(template.sib_id, recipients, all_params, test=test)

    if response:
        create_transaction(
            transaction_id=response.message_id,
            recipients=recipients,
            label=template_name,
            related=related,
            faked=test,
        )

    return response


def send_debug_email(template_name, recipients, params=None, test=False, related=None):
    """
    As an alternative, use the default django send_mail, mostly used for debugging
    and displaying email on the terminal.
    """

    if not isinstance(recipients, list):
        recipients = [recipients]

    simple_recipients = []
    for recipient in recipients:
        if isinstance(recipient, dict):
            simple_recipients.append(recipient["email"])
        else:
            simple_recipients.append(recipient)

    logger.debug(f"Sending email to {simple_recipients}")

    all_params = get_site_params()
    if params:
        all_params.update(params)

    django_send_mail(
        "Brevo Mail",
        f"Message utilisant le template {template_name} avec les "
        f"paramètres : {all_params} (TEST MODE: {test})",
        "no-reply@recoconseil.fr",
        simple_recipients,
        fail_silently=False,
    )

    create_transaction(
        transaction_id=f"FAKE-ID-{timezone.now()}",
        recipients=recipients,
        label=template_name,
        related=related,
        faked=True,
    )

    return True


def fetch_transaction_content(transaction_id):
    brevo = Brevo()

    emails = brevo.get_emails_from_transactionid(transaction_id)

    for email in emails.transactional_emails:
        return brevo.get_content_from_uuid(email.uuid)

    return None


def send_mail_filter_recipient(
    template_name, recipients, params=None, test=False, related=None
):
    if not isinstance(recipients, list):
        recipients = [recipients]

    white_listed_recipients = getattr(settings, "DEBUG_EMAIL_WHITELIST", [])
    to_really_send, to_debug_send = [], []
    for recipient in recipients:
        email = recipient if isinstance(recipient, str) else recipient["email"]
        (to_really_send if email in white_listed_recipients else to_debug_send).append(
            recipient
        )

    res_debug = (
        send_debug_email(
            template_name, to_debug_send, params=params, test=test, related=related
        )
        if len(to_debug_send) > 0
        else True
    )
    res_brevo = (
        brevo_email(
            template_name, to_really_send, params=params, test=test, related=related
        )
        if len(to_really_send) > 0
        else True
    )
    return res_brevo and res_debug


if settings.DEBUG:
    if getattr(settings, "BREVO_FORCE_DEBUG", False):
        send_email = send_mail_filter_recipient
    else:
        send_email = send_debug_email
else:
    send_email = brevo_email

# eof
