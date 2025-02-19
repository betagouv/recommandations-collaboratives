from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.db import models


class HitCountQuerySet(models.QuerySet):
    def for_content_object(self, content_object) -> models.QuerySet:
        content_type = ContentType.objects.get_for_model(content_object)
        return self.filter(
            content_object_ct=content_type, content_object_id=content_object.pk
        )

    def for_context_object(self, context_object) -> models.QuerySet:
        content_type = ContentType.objects.get_for_model(context_object)
        return self.filter(
            context_object_ct=content_type, context_object_id=context_object.pk
        )

    def for_user(self, user: User) -> models.QuerySet:
        return self.filter(hits__user=user)


class HitCountOnSiteManager(CurrentSiteManager.from_queryset(HitCountQuerySet)):
    use_in_migrations = False


class HitCountManager(models.Manager.from_queryset(HitCountQuerySet)):
    use_in_migrations = False
