import uuid

from django.contrib.auth import models as auth_models
from django.db import models
from django.urls import reverse
from django.utils import timezone
from urbanvitaliz.apps.projects import models as projects_models


class Invite(models.Model):
    """Invitation for a project"""

    class Meta:
        unique_together = ("email", "project", "role")

    INVITE_ROLES = (
        ("COLLABORATOR", "Collaborateur·rice"),
        ("SWITCHTENDER", "Aiguilleur·se"),
    )

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
    email = models.EmailField(max_length=254)

    inviter = models.ForeignKey(
        auth_models.User, null=True, on_delete=models.CASCADE, verbose_name="invitant"
    )
    project = models.ForeignKey(
        projects_models.Project,
        on_delete=models.CASCADE,
        verbose_name="projet",
        related_name="invites",
    )

    message = models.TextField(null=True, blank=True)

    role = models.CharField(max_length=20, choices=INVITE_ROLES, default="COLLABORATOR")

    def get_absolute_url(self):
        return reverse("invites-invite-details", args=[self.pk])
