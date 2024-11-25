from allauth.socialaccount import app_settings
from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "<str:provider_id>/",
        include(
            [
                path("login/", views.login, name="openid_connect_login"),
                path("login/callback/", views.callback, name="openid_connect_callback"),
            ]
        ),
    )
]

urlpatterns = [path(f"{app_settings.OPENID_CONNECT_URL_PREFIX}/", include(urlpatterns))]
