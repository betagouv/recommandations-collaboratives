from django.core.mail import mail_admins

from .models import EmailTemplate
from .sendinblue import SendInBlue


def send_email(template_name, recipients, params=None, test=False):
    sib = SendInBlue()
    try:
        template = EmailTemplate.objects.get(name__iexact=template_name)
    except EmailTemplate.DoesNotExist:
        mail_admins(
            subject="Unable to send email", message=f"{template_name} was not found !"
        )
        return False

    return sib.send_email(template.sib_id, recipients, params, test=test)
