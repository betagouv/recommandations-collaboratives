from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.functional import cached_property
from rest_framework.request import Request
from rest_framework.serializers import Serializer, ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from recoco.apps.home.utils import (
    UnavailableAccountException,
    find_verified_user_for_site,
)


class BaseSerializerMixin(Serializer):
    @property
    def request(self) -> Request:
        return self.context["request"]

    @cached_property
    def current_site(self) -> Site:
        return (
            self.request.site
            if hasattr(self.request, "site")
            else get_current_site(self.request)
        )

    @cached_property
    def current_user(self) -> User | None:
        return self.request.user if hasattr(self.request, "user") else None


def validate_email_for_site(email, site):
    """Refuse the email of an account that cannot be used on the site"""
    try:
        find_verified_user_for_site(email, site)
    except UnavailableAccountException as exc:
        raise ValidationError(str(exc)) from exc

    return email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token
