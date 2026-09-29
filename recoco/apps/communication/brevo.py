import logging

import sentry_sdk
import sib_api_v3_sdk as brevo_sdk
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from sib_api_v3_sdk.rest import ApiException

logger = logging.getLogger("main")


_TEMPLATE_DELIMITERS = ("{{", "}}", "{%", "%}", "{#", "#}")

# Deliberately a visible space: an invisible separator silently stops working
# if any stage of Brevo's pipeline strips or normalizes zero-width characters.
_DELIMITER_SEPARATOR = " "


def _break_template_delimiters(text):
    """Separate the two halves of every Django template delimiter.

    A single non-overlapping replace pass can leave a delimiter behind on
    overlapping/odd-length brace runs (e.g. "{{{7*7}}}" still contains "{{"
    after one pass), so this loops until no known delimiter remains.
    """
    previous = None
    while previous != text:
        previous = text
        for pair in _TEMPLATE_DELIMITERS:
            text = text.replace(pair, f"{pair[0]}{_DELIMITER_SEPARATOR}{pair[1]}")
    return text


def sanitize_brevo_params(value):
    """Neutralize Brevo/Django template syntax in outgoing params.

    User-controlled strings (note content, comments, names, etc.) can reach
    Brevo's own template renderer verbatim. Brevo's engine is Django-based,
    so `{{ }}`, `{% %}` and `{# #}` are all live syntax; a payload like
    `{{7*7}}` would be evaluated by Brevo, not us (a Brevo-side SSTI).
    Inserting a space inside any such delimiter stops Brevo from
    recognizing it as a template tag, at the cost of a visible space in the
    rare case where a user legitimately wrote one of those sequences.
    """
    if isinstance(value, str):
        return _break_template_delimiters(value)
    if isinstance(value, dict):
        return {
            (_break_template_delimiters(k) if isinstance(k, str) else k): (
                sanitize_brevo_params(v)
            )
            for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [sanitize_brevo_params(v) for v in value]
    return value


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

    def send_email(
        self,
        template_id,
        recipients,
        params=None,
        test=False,
        dry_run=False,
        sender_name=None,
    ):
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
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would have sent test template {template_id} "
                    f"to {recipients}"
                )
                return None
            return self.api_instance.send_test_template(template_id, send_test_email)
        else:
            send_to = [
                brevo_sdk.SendSmtpEmailTo(
                    name=recipient.get("name", "Utilisateur Recoconseil"),
                    email=recipient["email"],
                )
                for recipient in recipients
            ]

            # when the site defines no sender name, fall back on the default
            # identity configured in the settings
            sender = brevo_sdk.SendSmtpEmailSender(
                name=sender_name or settings.DEFAULT_SENDER_NAME,
                email=settings.DEFAULT_SENDER_EMAIL,
            )

            send_smtp_email = brevo_sdk.SendSmtpEmail(
                template_id=template_id,
                to=send_to,
                params=sanitize_brevo_params(params),
                sender=sender,
            )

            if dry_run:
                # Everything up to this point (template resolution, params
                # merging, payload construction) has run for real. Only the
                # actual HTTP call to Brevo is skipped.
                logger.info(
                    "[DRY RUN] Would have called Brevo send_transac_email "
                    f"with:\n{send_smtp_email}"
                )
                return None

            try:
                return self.api_instance.send_transac_email(send_smtp_email)
            except ApiException as e:
                print(
                    f"error sending email to users {','.join(str(recipient.id) for recipient in recipients if hasattr(recipient, 'id'))}"
                )
                sentry_sdk.capture_exception(e)

    def get_emails_from_transactionid(self, transaction_id):
        return self.api_instance.get_transac_emails_list(message_id=transaction_id)

    def get_content_from_uuid(self, uuid):
        return self.api_instance.get_transac_email_content(uuid=uuid)
