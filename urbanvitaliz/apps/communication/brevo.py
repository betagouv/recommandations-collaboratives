import sib_api_v3_sdk as brevo_sdk
from django.conf import settings


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
        if type(recipients) is not list:
            recipients = [recipients]

        if test:
            send_test_email = brevo_sdk.SendTestEmail(email_to=[recipients[0]["email"]])
            response = self.api_instance.send_test_template(
                template_id, send_test_email
            )
        else:
            send_to = [
                brevo_sdk.SendSmtpEmailTo(
                    name=recipient.get("name", "Utilisateur UrbanVitaliz"),
                    email=recipient["email"],
                )
                for recipient in recipients
            ]

            send_smtp_email = brevo_sdk.SendSmtpEmail(
                template_id=template_id, to=send_to, params=params
            )
            response = self.api_instance.send_transac_email(send_smtp_email)

        return response
