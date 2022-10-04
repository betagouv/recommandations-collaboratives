from django.contrib.auth import models as auth_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from markdownx.utils import markdownify
from urbanvitaliz.apps.addressbook import models as addressbook_models
from urbanvitaliz.apps.projects import models as projects_models


class NoteManager(models.Manager):
    pass


class NoteOnSiteManager(CurrentSiteManager, NoteManager):
    pass


class Note(models.Model):
    objects = NoteManager()
    on_site = NoteOnSiteManager()

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

    title = models.CharField(max_length=128, verbose_name="Titre de la note")
    content = models.TextField(default="")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related = GenericForeignKey("content_type", "object_id")

    def get_absolute_url(self):
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


project_ct = ContentType.objects.get_for_model(projects_models.Project)
user_ct = ContentType.objects.get_for_model(auth_models.User)
organization_ct = ContentType.objects.get_for_model(addressbook_models.Organization)
