from django.apps import AppConfig


class FeatureFlagConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "recoco.apps.feature_flag"
