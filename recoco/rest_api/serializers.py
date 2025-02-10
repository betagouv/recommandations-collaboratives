from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.functional import cached_property
from rest_framework.request import Request
from rest_framework.serializers import Serializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class BaseSerializerMixin(Serializer):
    @property
    def request(self) -> Request:
        return self.context["request"]

    @cached_property
    def current_site(self) -> Site:
        return self.request.site

    @cached_property
    def current_user(self) -> User | None:
        return self.request.user if hasattr(self.request, "user") else None


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        return token
