# encoding: utf-8

"""
Models for home application

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2021-11-15 14:44:55 CET
"""

from django.contrib.auth import models as auth
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.geomatics import models as geomatics


class UserProfileManager(models.Manager):
    """Manager for active UserProfile"""

    def get_queryset(self):
        return super().get_queryset().filter(deleted=None)


class DeletedUserProfileManager(models.Manager):
    """Manager for deleted UserProfile"""

    def get_queryset(self):
        return super().get_queryset().exclude(deleted=None)


class UserProfile(models.Model):
    """Represents the profile of a user"""

    objects = UserProfileManager()
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
    )

    organization_position = models.CharField(null=True, blank=True, max_length=200)

    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "profil utilisateur"
        verbose_name_plural = "profils utilisateurs"

    def __str__(self):
        return f"<UserProfile: {self.user.username}>"


class SiteConfiguration(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE)

    project_survey = models.ForeignKey("survey.Survey", on_delete=models.CASCADE)
    onboarding = models.ForeignKey("onboarding.Onboarding", on_delete=models.CASCADE)

    def __str__(self):
        return f"SiteConfiguration for '{self.site}'"


@receiver(post_save, sender=auth.User)
def create_user_profile(sender, instance, created, **kwargs):
    """register user profile creation when a user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)


# eof
