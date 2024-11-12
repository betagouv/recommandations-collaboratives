from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.utils.crypto import get_random_string


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def generate_state_param(self, state: dict) -> str:
        return get_random_string(32)
