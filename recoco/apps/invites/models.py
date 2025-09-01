import uuid

from django.contrib.auth import models as auth_models
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from recoco.apps.projects import models as projects_models


class InviteManager(models.Manager):
    def pending(self):
        return self.filter(accepted_on=None, refused_on=None)


class InviteOnSiteManager(CurrentSiteManager, InviteManager):
    pass


class Invite(models.Model):
    """Invitation for a project"""

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_accepted_or_refused",
                condition=(
                    Q(accepted_on=None, refused_on=None)
                    | Q(Q(accepted_on=None) & ~Q(refused_on=None))
                    | Q(~Q(accepted_on=None) & Q(refused_on=None))
                ),
            )
        ]

    INVITE_ROLES = (
        ("COLLABORATOR", "Participant·e"),
        ("SWITCHTENDER", "Conseiller·e"),
        ("OBSERVER", "Observateur·trice"),
    )

    objects = InviteManager()
    on_site = InviteOnSiteManager()

    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created_on = models.DateTimeField(
        default=timezone.now, verbose_name="date d'invitation", editable=False
    )

    accepted_on = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        editable=False,
        verbose_name="date d'acceptation",
    )
    refused_on = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        editable=False,
        verbose_name="date de refus",
    )

    email = models.EmailField(max_length=254)

    inviter = models.ForeignKey(
        auth_models.User, null=True, on_delete=models.CASCADE, verbose_name="invitant"
    )
    project = models.ForeignKey(
        projects_models.Project,
        on_delete=models.CASCADE,
        verbose_name="dossier",
        related_name="invites",
    )

    message = models.TextField(null=True, blank=True)

    role = models.CharField(max_length=20, choices=INVITE_ROLES, default="COLLABORATOR")

    def get_absolute_url(self):
        return reverse("invites-invite-details", args=[self.pk])

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)
