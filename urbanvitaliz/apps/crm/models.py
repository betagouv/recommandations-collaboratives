from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from markdownx.utils import markdownify
from taggit.managers import TaggableManager

from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models

from . import apps


# We need the permission to be associated to the site and not to the projects
@receiver(post_migrate)
def create_site_permissions(sender, **kwargs):
    if sender.name != apps.CrmConfig.name:
        return

    site_ct = ContentType.objects.get(app_label="sites", model="site")

    auth_models.Permission.objects.get_or_create(
        codename="use_crm",
        name="Can use the CRM for site",
        content_type=site_ct,
    )


#
# ProjectAnnotations


class ProjectAnnotationsManager(models.Manager):
    """Manager for all project annotations"""

    pass


class ProjectAnnotationsOnSiteManager(CurrentSiteManager, ProjectAnnotationsManager):
    """Manager for on site project annotations"""

    pass


class ProjectAnnotations(models.Model):
    """Represents a collection of annotations to a project"""

    objects = ProjectAnnotationsManager()
    on_site = ProjectAnnotationsOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    project = models.OneToOneField(
        projects_models.Project,
        on_delete=models.CASCADE,
        related_name="crm_annotations",
    )
    tags = TaggableManager(blank=True)

    created_on = models.DateTimeField(default=timezone.now)
    updated_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "project annotation"
        verbose_name_plural = "project annotations"

    def __str__(self):
        return f"CRM annotations for {self.project.name}"


class NoteManager(models.Manager):
    pass


class NoteOnSiteManager(CurrentSiteManager, NoteManager):
    pass


class Note(models.Model):

    PHONE_CALL = 0
    EMAIL = 1
    USER_TEST = 2

    KIND_CHOICES = (
        (PHONE_CALL, "Appel Téléphonique"),
        (EMAIL, "Email"),
        (USER_TEST, "Test utilisateur"),
    )
    objects = NoteManager()
    on_site = NoteOnSiteManager()

    kind = models.IntegerField(
        choices=KIND_CHOICES,
        blank=True,
        null=True,
        verbose_name="Type de contact",
    )

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="Date de création"
    )
    updated_on = models.DateTimeField(
        default=timezone.now, verbose_name="Dernière mise à jour"
    )

    sticky = models.BooleanField(default=False, verbose_name="Épingler")

    created_by = models.ForeignKey(
        auth_models.User, on_delete=models.CASCADE, related_name="crm_notes_created"
    )

    title = models.CharField(
        max_length=128, verbose_name="Titre de la note", blank=True, null=True
    )
    content = models.TextField(default="")

    tags = TaggableManager(blank=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related = GenericForeignKey("content_type", "object_id")

    def get_absolute_url(self):
        project_ct = ContentType.objects.get_for_model(projects_models.Project)
        user_ct = ContentType.objects.get_for_model(auth_models.User)
        organization_ct = ContentType.objects.get_for_model(
            addressbook_models.Organization
        )

        try:
            url = {
                user_ct: reverse("crm-user-details", args=[self.object_id]),
                project_ct: reverse("crm-project-details", args=[self.object_id]),
                organization_ct: reverse(
                    "crm-organization-details", args=[self.object_id]
                ),
            }[self.content_type]
        except KeyError:
            url = self.related.get_absolute_url()

        return url

    @property
    def content_rendered(self):
        """Return content as markdown"""
        return markdownify(self.content)
