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
    """Uses sendinblue service to send an email using the given template and params"""
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
    """As an alternative, use the default django send_mail, mostly used for debugging and
    displaying email on the terminal"""
    if type(recipients) is not list:
        recipients = [recipients]

    simple_recipients = []
    for recipient in recipients:
        if type(recipient) is dict:
            simple_recipients.append(recipient["email"])
        else:
            simple_recipients.append(recipient)

    print(f"Sending to {simple_recipients}")

    django_send_mail(
        "SIB Mail",
        f"Message utilisant le template {template_name} avec les paramètres : {params} (TEST MODE: {test})",
        "no-reply@urbanvitaliz.fr",
        simple_recipients,
        fail_silently=False,
    )
    return True


if settings.DEBUG and getattr(settings, "SENDINBLUE_FORCE_DEBUG", False):
    send_email = send_debug_email
else:
    send_email = send_in_blue_email

# eof
