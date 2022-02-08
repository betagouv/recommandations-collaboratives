# encoding: utf-8

"""
api for sending emails

Always use the send_email function that can be implemented as:

- a debug version through the terminal
- a production version through send in blue


authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
updated: 2022-02-03 16:19:24 CET
"""

from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail import send_mail as django_send_mail

from .models import EmailTemplate
from .sendinblue import SendInBlue


def send_in_blue_email(template_name, recipients, params=None, test=False):
    sib = SendInBlue()
    try:
        template = EmailTemplate.objects.get(name__iexact=template_name)
    except EmailTemplate.DoesNotExist:
        mail_admins(
            subject="Unable to send email", message=f"{template_name} was not found !"
        )
        return False

    return sib.send_email(template.sib_id, recipients, params, test=test)


def send_debug_email(template_name, recipients, params=None, test=False):
    if type(recipients) is not list:
        recipients = [recipients]

    django_send_mail(
        "SIB Mail",
        f"Message utilisant le template {template_name} avec les paramètres : {params} (TEST MODE: {test})",
        "no-reply@urbanvitaliz.fr",
        recipients,
        fail_silently=False,
    )
    return True


if settings.DEBUG and not (settings.SENDINBLUE_API_KEY):
    send_email = send_debug_email
else:
    send_email = send_in_blue_email

# eof
