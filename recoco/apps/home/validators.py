import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator


class UppercaseAndDigitPasswordValidator:
    """
    Validate that the password contains at least an uppercase character
    and a digit.
    """

    def validate(self, password, user=None):
        has_digit = bool(re.search(r"\d", password))
        has_uppercase = bool(re.search(r"[A-Z]", password))

        if has_digit and has_uppercase:
            return

        raise ValidationError(
            self.get_error_message(),
            code="password_contains_uppercase_and_number",
        )

    def get_error_message(self):
        return "Votre mot de passe doit contenir au moins une majuscule et une chiffre."

    def get_help_text(self):
        return "Votre mot de passe doit contenir au moins une majuscule et une chiffre."


class EmailValidatorForBrevo(EmailValidator):
    def __call__(self, value):
        # The maximum length of an email is 320 characters per RFC 3696
        # section 3 but verriden to 254 for Brevo
        if not value or "@" not in value or len(value) > 254:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        user_part, domain_part = value.rsplit("@", 1)

        # 64 caracters because of brevo
        if not self.user_regex.match(user_part) or len(user_part) > 64:
            raise ValidationError(self.message, code=self.code, params={"value": value})

        if (
            domain_part not in self.domain_allowlist
            and not self.validate_domain_part(domain_part)
            or len(domain_part) > 63
        ):
            raise ValidationError(self.message, code=self.code, params={"value": value})
