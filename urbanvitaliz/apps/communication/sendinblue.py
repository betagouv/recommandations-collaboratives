import sib_api_v3_sdk
from django.conf import settings
from sib_api_v3_sdk.rest import ApiException


class SendInBlue:
    def __init__(self):
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key["api-key"] = settings.SENDINBLUE_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
            sib_api_v3_sdk.ApiClient(self.configuration)
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
            send_test_email = sib_api_v3_sdk.SendTestEmail(email_to=recipients)
            response = self.api_instance.send_test_template(
                template_id, send_test_email
            )
        else:
            send_to = [
                sib_api_v3_sdk.SendSmtpEmailTo(email=recipient)
                for recipient in recipients
            ]
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                template_id=template_id, to=send_to, params=params
            )
            response = self.api_instance.send_transac_email(send_smtp_email)

        return response
