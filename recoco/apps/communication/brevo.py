import sib_api_v3_sdk as brevo_sdk
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


class Brevo:
    def __init__(self):
        self.configuration = brevo_sdk.Configuration()
        self.configuration.api_key["api-key"] = settings.BREVO_API_KEY
        self.api_instance = brevo_sdk.TransactionalEmailsApi(
            brevo_sdk.ApiClient(self.configuration)
        )

    def get_templates(self):
        api_response = self.api_instance.get_smtp_templates(
            template_status="true", sort="asc"
        )

        return api_response.templates

    def send_email(self, template_id, recipients, params=None, test=False):
        if not isinstance(recipients, list):
            recipients = [recipients]

        # Check email adresses
        for recipient in recipients:
            email = recipient if isinstance(recipient, str) else recipient["email"]
            try:
                validate_email(email)
            except ValidationError as e:
                raise ValidationError(f"Incorrect email address: {email}") from e

        if test:
            send_test_email = (
                brevo_sdk.SendTestEmail()
            )  # XXX disabled to default to test list;
            # email_to=[recipients[0]["email"]])
            response = self.api_instance.send_test_template(
                template_id, send_test_email
            )
        else:
            send_to = [
                brevo_sdk.SendSmtpEmailTo(
                    name=recipient.get("name", "Utilisateur Recoconseil"),
                    email=recipient["email"],
                )
                for recipient in recipients
            ]

            send_smtp_email = brevo_sdk.SendSmtpEmail(
                template_id=template_id, to=send_to, params=params
            )

            response = self.api_instance.send_transac_email(send_smtp_email)

        return response

    def get_emails_from_transactionid(self, transaction_id):
        return self.api_instance.get_transac_emails_list(message_id=transaction_id)

    def get_content_from_uuid(self, uuid):
        return self.api_instance.get_transac_email_content(uuid=uuid)
