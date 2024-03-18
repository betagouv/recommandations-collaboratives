# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET
"""

from actstream.managers import ActionManager
from django.contrib.auth import models as auth
from django.contrib.auth.models import Permission
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import force_str
from guardian.core import ObjectPermissionChecker
from guardian.ctypes import get_content_type
from guardian.managers import BaseObjectPermissionManager
from guardian.models import (
    BaseGenericObjectPermission,
    GroupObjectPermissionAbstract,
    GroupObjectPermissionBase,
    UserObjectPermissionAbstract,
    UserObjectPermissionBase,
)
from phonenumber_field.modelfields import PhoneNumberField
from taggit.managers import TaggableManager
from recoco.apps.addressbook import models as addressbook_models
from recoco.apps.geomatics import models as geomatics

SITE_GROUP_PERMISSIONS = {
    "staff": (
        "sites.moderate_projects",
        "sites.list_projects",
        "sites.delete_projects",
        "sites.manage_resources",
        "sites.use_crm",
        "sites.use_addressbook",
        "sites.use_project_tags",
    ),
    "admin": ("sites.manage_surveys",),
    "advisor": ("sites.list_projects",),
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

    previous_login_at = models.DateTimeField(null=True, blank=True)

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

    project_survey = models.ForeignKey(
        "survey.Survey", null=True, on_delete=models.SET_NULL
    )
    onboarding = models.ForeignKey(
        "onboarding.Onboarding", null=True, on_delete=models.SET_NULL
    )
    sender_email = models.EmailField(
        help_text="Adresse de l'expéditeur pour les emails automatiques"
    )
    sender_name = models.CharField(
        help_text="Nom de l'expéditeur pour les emails automatiques", max_length=30
    )
    contact_form_recipient = models.EmailField(
        help_text="Adresse d'expédition pour le formulaire de contact"
    )

    def logo_upload_path(self, filename):
        return f"images/{self.site.pk}/logo/{filename}"
    
    email_logo = models.ImageField(
        verbose_name="Logo utilisé pour les emails automatiques", 
        help_text="Veuillez fournir une image d'une largeur maximale de 600 pixels et d'un ratio de 4:3.",
        null=True, blank=True, upload_to=logo_upload_path
    )

    crm_available_tags = TaggableManager(
        blank=True,
        verbose_name="Étiquettes projets disponibles dans le CRM",
        help_text=(
            "Liste de tags séparés par une virgule. "
            "Attention, veillez à ne pas retirer un tag utilisé dans un projet, "
            "celui-ci ne pourra plus être retiré depuis le CRM"
        ),
    )
    reminder_interval = models.IntegerField(
        default=6 * 7, verbose_name="Interval des rappels", help_text="en jours"
    )

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
### and honours current site admins


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

# Permission getter, patched to honour staff group


def get_user_perms(self, obj):
    # XXX This introduces a security flaw where one can pass an object from another
    # site than the current one. This leads to a false positive and gives cross-site
    # privilege elevation.
    # For the sake of simplicity, we decided to keep it as is, given we're in control
    # of all calls.

    # FIXME Refactor to move that (circular import)
    from recoco import utils as uv_utils

    ctype = get_content_type(obj)

    if uv_utils.is_staff_for_site(self.user):
        return list(
            Permission.objects.filter(
                content_type=ctype,
            ).values_list("codename", flat=True)
        )

    return ObjectPermissionChecker.original_get_user_perms(self, obj)


ObjectPermissionChecker.original_get_user_perms = ObjectPermissionChecker.get_user_perms
ObjectPermissionChecker.get_user_perms = get_user_perms


# Override cache key identity using site
def get_local_cache_key_with_site(self, obj):
    ctype = get_content_type(obj)
    site = Site.objects.get_current()
    return (ctype.id, force_str(obj.pk), force_str(site.pk))


ObjectPermissionChecker.original_get_local_cache_key = (
    ObjectPermissionChecker.get_local_cache_key
)
ObjectPermissionChecker.get_local_cache_key = get_local_cache_key_with_site


# eof
