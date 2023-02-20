# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET
"""

from actstream.managers import ActionManager
from django.contrib.auth import models as auth
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from guardian.core import ObjectPermissionChecker
from guardian.managers import BaseObjectPermissionManager
from guardian.models import (
    BaseGenericObjectPermission,
    GroupObjectPermissionAbstract,
    GroupObjectPermissionBase,
    UserObjectPermissionAbstract,
    UserObjectPermissionBase,
)
from phonenumber_field.modelfields import PhoneNumberField
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics


SITE_GROUP_PERMISSIONS = {
    "staff": (),
    "admin": (),
    "advisor": (),
}


class SiteActionManager(CurrentSiteManager, ActionManager):
    pass


class UserProfileManager(models.Manager):
    """Manager for active UserProfile"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class UserProfileOnSiteManager(CurrentSiteManager, UserProfileManager):
    """Manager for active UserProfile on the current site"""

    pass


class DeletedUserProfileManager(models.Manager):
    """Manager for deleted UserProfile"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class UserProfile(models.Model):
    """Represents the profile of a user"""

    objects = UserProfileManager()
    on_site = UserProfileOnSiteManager()
    deleted_objects = DeletedUserProfileManager()

    user = models.OneToOneField(
        auth.User, on_delete=models.CASCADE, related_name="profile"
    )

    departments = models.ManyToManyField(
        geomatics.Department, related_name="user_profiles", blank=True
    )

    organization = models.ForeignKey(
        addressbook_models.Organization,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="registered_profiles",
    )

    sites = models.ManyToManyField(Site)

    phone_no = PhoneNumberField(blank=True)

    organization_position = models.CharField(null=True, blank=True, max_length=200)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "profil utilisateur"
        verbose_name_plural = "profils utilisateurs"

    def __str__(self):
        return f"<UserProfile: {self.user.username}>"


class SiteConfiguration(models.Model):
    site = models.OneToOneField(
        Site, on_delete=models.CASCADE, related_name="configuration"
    )

    project_survey = models.ForeignKey("survey.Survey", on_delete=models.CASCADE)
    onboarding = models.ForeignKey("onboarding.Onboarding", on_delete=models.CASCADE)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=30)

    def __str__(self):
        return f"SiteConfiguration for '{self.site}'"


@receiver(post_save, sender=auth.User)
def create_user_profile(sender, instance, created, **kwargs):
    """register user profile creation when a user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


#################################################################
# Django Guardian
#################################################################
class BaseObjectPermissionManagerOnSite(
    CurrentSiteManager, BaseObjectPermissionManager
):
    def get_or_create(self, defaults=None, **kwargs):
        if "site" not in kwargs.keys():
            kwargs["site"] = Site.objects.get_current()

        # XXX Not sure if needed -- better coverage needed to improve
        if defaults and "site" not in defaults.keys:
            kwargs["site"] = Site.objects.get_current()

        return super().get_or_create(defaults, **kwargs)

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        for obj in objs:
            if not getattr(obj, "site", None):
                obj.site = Site.objects.get_current()

        return super().bulk_create(objs, batch_size, ignore_conflicts)


class UserObjectPermissionManagerOnSite(BaseObjectPermissionManagerOnSite):
    pass


class UserObjectPermissionOnSite(UserObjectPermissionBase, BaseGenericObjectPermission):
    """Override default model to take the current site into account"""

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    objects = UserObjectPermissionManagerOnSite()

    class Meta(UserObjectPermissionBase.Meta, BaseGenericObjectPermission.Meta):
        abstract = False
        indexes = [
            *UserObjectPermissionAbstract.Meta.indexes,
            models.Index(fields=["content_type", "object_pk", "user", "site"]),
        ]
        unique_together = ["user", "permission", "object_pk", "site"]


class GroupObjectPermissionManagerOnSite(BaseObjectPermissionManagerOnSite):
    pass


class GroupObjectPermissionOnSite(
    GroupObjectPermissionBase, BaseGenericObjectPermission
):
    """Override default model to take the current site into account"""

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    objects = GroupObjectPermissionManagerOnSite()

    class Meta(GroupObjectPermissionBase.Meta, BaseGenericObjectPermission.Meta):
        abstract = False
        indexes = [
            *GroupObjectPermissionAbstract.Meta.indexes,
            models.Index(fields=["content_type", "object_pk", "group", "site"]),
        ]
        unique_together = ["group", "permission", "object_pk", "site"]


### Monkey patch guardian behaviour so it returns current site permission

# Users
def get_user_filters_with_sites(self, obj):
    """Monkey patched method to force filtering by current site.
    Should be removed as soon as guardian supports the site framework
    """
    filters = ObjectPermissionChecker.original_get_user_filters(self, obj)
    # Force filtering by current_site
    filters["userobjectpermissiononsite__site"] = Site.objects.get_current()
    return filters


ObjectPermissionChecker.original_get_user_filters = (
    ObjectPermissionChecker.get_user_filters
)
ObjectPermissionChecker.get_user_filters = get_user_filters_with_sites


# Groups
def get_group_filters_with_sites(self, obj):
    """Monkey patched method to force filtering by current site.
    Should be removed as soon as guardian supports the site framework
    """
    filters = ObjectPermissionChecker.original_get_group_filters(self, obj)
    # Force filtering by current_site
    filters["groupobjectpermissiononsite__site"] = Site.objects.get_current()
    return filters


ObjectPermissionChecker.original_get_group_filters = (
    ObjectPermissionChecker.get_group_filters
)
ObjectPermissionChecker.get_group_filters = get_group_filters_with_sites


# eof
