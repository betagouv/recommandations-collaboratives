import re

from django.core.exceptions import ValidationError


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
