from allauth.account import app_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username


class UVAccountAdapter(DefaultAccountAdapter):
    def populate_username(self, request, user):
        """
        Fills in a valid username based on email, if required and missing.  If the
        username is already present it is assumed to be valid
        (unique).
        """
        email = user_email(user)

        if app_settings.USER_MODEL_USERNAME_FIELD:
            user_username(user, email)
