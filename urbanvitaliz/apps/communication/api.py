from django.conf import settings
from django.core.mail import mail_admins
from django.core.mail import send_mail as django_send_mail

from .models import EmailTemplate
from .sendinblue import SendInBlue


def send_email(template_name, recipients, params=None, test=False):
    if not type(recipients) == "list":
        recipients = [recipients]

    # If we are in debug, use standard django send_email so it is printed
    # onto the terminal
    if settings.DEBUG and False:
        django_send_mail(
            "SIB Mail",
            f"Message utilisant le template {template_name} avec les paramètres : {params} (TEST MODE: {test})",
            "no-reply@urbanvitaliz.fr",
            recipients,
            fail_silently=False,
        )
        return True

    sib = SendInBlue()
    try:
        template = EmailTemplate.objects.get(name__iexact=template_name)
    except EmailTemplate.DoesNotExist:
        mail_admins(
            subject="Unable to send email", message=f"{template_name} was not found !"
        )
        return False

    return sib.send_email(template.sib_id, recipients, params, test=test)
