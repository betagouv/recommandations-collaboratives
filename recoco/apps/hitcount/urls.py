from django.urls import path

from .views import HitView

urlpatterns = [
    path("hit/", HitView.as_view(), name="api_hit"),
]
